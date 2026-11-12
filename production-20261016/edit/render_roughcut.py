#!/usr/bin/env python3
"""Offline, explicit-gated FFmpeg rough cut. Never reads a running capture by default."""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

FFMPEG = '/Users/USER/.local/bin/ffmpeg'
FFPROBE = '/Volumes/EXTERNAL/自媒体/motion-sample-20261012/v3-remotion/node_modules/@remotion/compositor-darwin-arm64/ffprobe'
FONT = '/System/Library/Fonts/STHeiti Medium.ttc'
ROOT = pathlib.Path(__file__).resolve().parent
BASE = ROOT.parent
FORBIDDEN = {'recording-check.mov', 'recording-check-workbuddy.mov', '01-finder-open-original.mov'}


def instant(t):
    return dt.datetime.fromisoformat(t.replace('Z', '+00:00'))


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(argv, log):
    p = subprocess.run(argv, capture_output=True, text=True)
    log.write_text(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(f'FFmpeg failed ({p.returncode}); see {log}')


def crop_filter(crop):
    if crop is None:
        return ''
    if len(crop) != 4 or any(not isinstance(n, int) or n < 0 for n in crop):
        raise ValueError('crop must be [x,y,width,height] nonnegative integer pixels')
    x, y, w, h = crop
    if not w or not h or w % 2 or h % 2:
        raise ValueError('crop width/height must be positive and even')
    return f'crop={w}:{h}:{x}:{y},'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--edl', default=str(ROOT / 'edl-draft.json'))
    ap.add_argument('--render', action='store_true')
    ap.add_argument('--output-dir')
    args = ap.parse_args()
    edl = json.loads(pathlib.Path(args.edl).read_text())
    total = sum(s['duration_s'] for s in edl['shots'])
    if total != edl['output']['duration_s']:
        raise ValueError('EDL sum differs from expected output duration')
    start = 0
    for shot in edl['shots']:
        if shot['mode'] != 'editorial_card' and abs(sum(s['duration_s'] for s in shot['segments']) - shot['duration_s']) > .001:
            raise ValueError(f"segment duration mismatch: {shot['id']}")
        print(f"{shot['id']}: {start:.3f}–{start + shot['duration_s']:.3f}s {shot['label']}")
        start += shot['duration_s']
    if not args.render:
        print('PLAN ONLY. No media opened or probed; draft wallclocks/crops need final-source review.')
        return
    src = edl['finalized_source']
    if not (src['confirmed_finalized'] and edl['timing_verified'] and edl['crops_verified']):
        raise ValueError('Render blocked: finalized source, event timing, and crops must all be explicitly verified')
    if not src['path'] or not src['creation_time_utc'] or not args.output_dir:
        raise ValueError('Render requires source absolute path, creation_time, and new output directory')
    video = pathlib.Path(src['path']).resolve()
    if video.name in FORBIDDEN or video.parent != (BASE / 'raw').resolve():
        raise ValueError('Source outside approved raw directory or explicitly excluded')
    if not video.is_file():
        raise FileNotFoundError(video)
    origin = instant(src['creation_time_utc'])
    probe = subprocess.run([FFPROBE, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(video)], cwd=str(pathlib.Path(FFPROBE).parent), capture_output=True, text=True)
    if probe.returncode:
        raise RuntimeError('Finalized-source probe failed; do not render')
    metadata = json.loads(probe.stdout)
    source_duration = float(metadata['format']['duration'])
    video_stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    for shot in edl['shots']:
        for seg in shot['segments']:
            offset = (instant(seg['wallclock_start_utc']) - origin).total_seconds()
            if offset < 0 or offset + seg['duration_s'] > source_duration:
                raise ValueError(f"{shot['id']}: source interval outside finalized recording")
            if seg['crop']:
                x, y, w, h = seg['crop']
                if x + w > video_stream['width'] or y + h > video_stream['height']:
                    raise ValueError(f"{shot['id']}: crop exceeds actual frame")
    dest = pathlib.Path(args.output_dir).resolve()
    dest.mkdir(parents=True, exist_ok=False)
    before = (BASE / 'evidence/credits-before-and-version.png').resolve()
    source_hash = digest(video)
    commands = []
    timeline = []
    cursor = 0
    rendered = []
    for shot in edl['shots']:
        sid = shot['id']
        label = dest / f'{sid}-label.txt'
        note = dest / f'{sid}-note.txt'
        label.write_text(shot['label'])
        note.write_text(shot['note'])
        parts = []
        for index, seg in enumerate(shot['segments']):
            offset = (instant(seg['wallclock_start_utc']) - origin).total_seconds()
            if offset < 0:
                raise ValueError(f'{sid}: wallclock precedes recording creation_time')
            segfile = dest / f'{sid}-{index:02d}.mp4'
            vf = crop_filter(seg['crop']) + 'scale=1016:1320:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:300:color=0x11151b,setsar=1,fps=30,format=yuv420p'
            argv = [FFMPEG, '-hide_banner', '-n', '-ss', str(offset), '-i', str(video), '-t', str(seg['duration_s']), '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-movflags', '+faststart', str(segfile)]
            if shot['mode'] == 'credits':
                # Distinct real-before still and real-after video, clearly separated.
                graph = ('[0:v]' + crop_filter(shot['before_crop']) + 'scale=972:420:force_original_aspect_ratio=decrease,pad=1080:800:(ow-iw)/2:150:color=0x11151b,setsar=1,fps=30[b];' +
                         '[1:v]' + crop_filter(seg['crop']) + 'scale=972:420:force_original_aspect_ratio=decrease,pad=1080:1120:(ow-iw)/2:120:color=0x11151b,setsar=1,fps=30[a];[b][a]vstack=inputs=2,format=yuv420p[v]')
                argv = [FFMPEG, '-hide_banner', '-n', '-loop', '1', '-i', str(before), '-ss', str(offset), '-i', str(video), '-filter_complex', graph, '-map', '[v]', '-t', str(seg['duration_s']), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', str(segfile)]
            run(argv, dest / f'{sid}-{index:02d}.log')
            commands.append(argv)
            parts.append(segfile)
        if shot['mode'] == 'editorial_card':
            segfile = dest / f'{sid}-card.mp4'
            argv = [FFMPEG, '-hide_banner', '-n', '-f', 'lavfi', '-i', 'color=c=0x11151b:s=1080x1920:r=30', '-t', str(shot['duration_s']), '-an', '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(segfile)]
            run(argv, dest / f'{sid}-card.log')
            commands.append(argv)
            parts.append(segfile)
        listing = dest / f'{sid}-concat.txt'
        listing.write_text(''.join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in parts))
        shotfile = dest / f'{sid}.mp4'
        vf = (f"drawtext=fontfile='{FONT}':textfile='{label}':fontsize=38:fontcolor=white:x=54:y=78," +
              f"drawtext=fontfile='{FONT}':textfile='{note}':fontsize=30:fontcolor=0xc5ccd5:x=54:y=1710:line_spacing=14")
        if shot['mode'] == 'editorial_card':
            vf = f"drawtext=fontfile='{FONT}':textfile='{label}':fontsize=42:fontcolor=white:x=54:y=390,drawtext=fontfile='{FONT}':textfile='{note}':fontsize=34:fontcolor=0xc5ccd5:x=54:y=560:line_spacing=24"
        elif shot['mode'] == 'credits':
            before_label = dest / 'S9-before-label.txt'
            after_label = dest / 'S9-after-label.txt'
            before_label.write_text('测试前')
            after_label.write_text('测试后')
            vf += f",drawtext=fontfile='{FONT}':textfile='{before_label}':fontsize=32:fontcolor=white:x=54:y=620,drawtext=fontfile='{FONT}':textfile='{after_label}':fontsize=32:fontcolor=white:x=54:y=1400"
        argv = [FFMPEG, '-hide_banner', '-n', '-f', 'concat', '-safe', '0', '-i', str(listing), '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30', str(shotfile)]
        run(argv, dest / f'{sid}-labels.log')
        commands.append(argv)
        timeline.append({'shot': sid, 'output_in_s': cursor, 'output_out_s': cursor + shot['duration_s'], 'segments': shot['segments'], 'editor_label': shot['label']})
        cursor += shot['duration_s']
        rendered.append(shotfile)
    listing = dest / 'all-shots-concat.txt'
    listing.write_text(''.join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in rendered))
    final = dest / 'WorkBuddy_实测_无配音粗剪_1080x1920_v1.mp4'
    argv = [FFMPEG, '-hide_banner', '-n', '-f', 'concat', '-safe', '0', '-i', str(listing), '-an', '-c:v', 'copy', '-movflags', '+faststart', str(final)]
    run(argv, dest / 'concat.log')
    commands.append(argv)
    if digest(video) != source_hash:
        raise RuntimeError('Source hash changed during render; do not approve output')
    report = {'status': 'RENDERED_PENDING_FINAL_VISUAL_AND_DECODE_QA', 'source': str(video), 'source_metadata': metadata, 'source_sha256': source_hash, 'output': str(final), 'output_sha256': digest(final), 'expected_duration_s': total, 'timeline': timeline, 'commands': commands, 'edl': edl}
    (dest / 'render-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(final)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)

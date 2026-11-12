# 本单真实素材粗剪准备

本目录只预备脚本及EDL；未读取正在录制的02文件，也未导出成片。

主agent给出已最终落盘的02绝对路径与creation_time后，复制edl-draft.json为新的edl-final.json，填写finalized_source，核对真实帧并更新每镜头crop与切点。确认实际片段内容符合标签后，才置timing_verified/crops_verified=true。若关键内容未录入，删除该镜头或改为明确的编辑问题说明，不能自动将计划当已录到。

时长35秒：S2 3秒、S3 3秒、S4 6秒、S5 6秒、S6 3秒、S7 6秒、S9 4秒、S10 4秒。S1缺失，S8跳过。缺口播稿，不声称已按段落对位。S5明确原Q2中止，S6明确Q3补救，S7明确是电脑HTML预览且手机未测。S4使用后续复看清晰画面，不冒充完成时刻。

脚本render_roughcut.py默认仅输出EDL时间结构，不读取媒体。只有显式--render且三个确认字段均通过才接触主片。需要使用现成ffmpeg，未安装任何工具/网络依赖。源片只读；输出采用新目录和ffmpeg -n防覆盖。

准备检查：`python3 render_roughcut.py --edl edl-draft.json`

收到并确认原片后：`python3 render_roughcut.py --edl edl-final.json --render --output-dir 绝对路径的新导出目录`

所有标签会显式标“编辑标签/编辑记录”，避免仿产品界面。S10为单独的编辑说明卡，不冒充WorkBuddy输出。无需原片字幕，也不添加配音、BGM、夸张特效。默认全景只作草案兜底，正式执行前仍要求人工确认crop；不能默认中心裁切导致字被截断。

记录的墙钟时刻仅为父agent提供的导航，必须以最终creation_time换算与真实帧复核。文件ctime/mtime不能替代视频媒体creation_time，视频开始时刻与命令启动时间也不能混用。若元数据基准无法对应实际事件，暂停裁切并如实报告，不拼接错误轮次。

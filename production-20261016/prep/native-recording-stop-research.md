# 原生录屏正常停止：只读研究（2026-10-16）

范围：本机 `/usr/sbin/screencapture` 的usage与man、Apple官方支持资料。没有操作UI、发送任何信号、读取/修改正在录制的文件、查询其他会话/个人资料，也没有试按键或启动另一录制。

## 可确认事实

- 本机usage与man记载：`-v`录屏，`-V<seconds>`限制录制秒数；`-U`仅为交互模式显示工具栏。没有写非交互CLI的stdin正常停止键、信号保存协议或另一个停止命令。`-h`实际为未知选项并以1退出，只打印usage；不启动捕获。原始输出见`screencapture-local-documentation.json`。
- [Apple《How to record the screen on Mac》](https://support.apple.com/en-us/102618)，页面发布日期2026-09-14：对Screenshot录制，可点击菜单栏停止按钮或使用Command-Control-Esc正常停止，然后保存录制。
- [Apple QuickTime Player用户指南](https://support.apple.com/guide/quicktime-player/record-your-screen-qtp97b08e666/mac)：Screenshot录屏同样通过菜单栏停止按钮结束。
- 上述Apple页面讲Screenshot/QuickTime界面录制；未明确承诺对当前非交互`/usr/sbin/screencapture -v -V1800 -l26913 -k ...`进程可用。不能把这层适用性推断当已验证。

## 当前录制推荐

主agent反馈：Ctrl-C曾使Finder段exit1且文件未保存；Command-Control-Esc对当前office录制未生效。因此不再尝试Ctrl-C、信号或猜测stdin按键。

只有在当前菜单栏能识别“Stop Recording/停止录制”且确认属于本次录制时，点击该控制才是Apple资料给出的正常提前停止途径；该行为由操作UI的主agent自行核实执行，本研究未确认当前控制是否存在。

若当前没有可识别的对应停止控制，可靠方案是保留现有进程，让原来的`-V1800`期限自动结束。主agent估计结束时间约2026-10-16 01:57 UTC，此时间仅引自主agent，不是本研究重查进程得出。正常到期后再核退出状态、目标文件存在、尺寸时长与完整解码；在那之前不读正在写入的文件。

不建议另开Shift-Command-5或QuickTime的新录制去尝试接管CLI，不保证会控制同一录制；不建议终止或杀进程来“保存”，现有官方与本机文档未提供可靠证据支持。

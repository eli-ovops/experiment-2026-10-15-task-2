# 安全原片检查与S9方案（2026-10-16）

仅使用主agent明确放行的 `raw/window-recording-check.mov` 与 `evidence/credits-before-and-version.png`。没有读取两份误录桌面的 `recording-check.mov`、`recording-check-workbuddy.mov` 或其截图，没有读取正在写入的02-office录制。

## 01原片缺失

指定 `raw/01-finder-open-original.mov` 在workspace路径不存在，ffprobe/ffmpeg均返回“No such file or directory”。主agent随后确认：Finder录制Ctrl-C后exit1且没有落盘，可能SIGINT被原生工具视为取消。此为真实录制问题，原片不存在，S1右键菜单、选择WorkBuddy与片尾进入窗口均没有可用源时间码，不应凭截图或计划补造。没有推断系统菜单被录入或遗漏，因该录屏根本未取得。

## 可用窗口验证片

绝对路径：`/Users/USER/Documents/Codex/2026-10-15/task-2/production-20261016/raw/window-recording-check.mov`

- 时长2.993333秒，1552×1012，H.264/yuv420p，无音轨，171帧；VFR平均约56.716fps（3800/67），不是固定60fps。creation_time：2026-10-16T01:14:50Z。
- ffprobe读取成功，ffmpeg全片解码返回0；null封装输出产生non-monotonic DTS警告，应在粗剪按真实帧率来源记录后明确转恒定30fps，不能写“检查全无报错”。未发现输入解码损坏错误。没有桌面播放器实际播放检查，因此证据等级为“可完整解码并已查看实际抽帧”，不声称已在播放器全片审看。
- 已看t≈1秒实际帧：仅WorkBuddy首页及账户菜单，版本V5.8.2、体验版、积分余额511.2清晰；可作版本/积分前证据或S9测试前画面。并非Excel窗口，无Finder右键菜单，不可用于S1或S2。
- 安全抽帧：`prep/qa/window-check-safe-t1.png`；0/1/2秒联系表：`prep/qa/window-check-contact-0-1-2s.png`，均由此已放行窗口验证片生成。

## 积分截图与S9可执行方案

截图绝对路径：`/Users/USER/Documents/Codex/2026-10-15/task-2/production-20261016/evidence/credits-before-and-version.png`，1552×1012。

已肉眼核对：左上WorkBuddy V5.8.2；账户弹层显示“套餐 体验版”“积分余额 511.2”。这是测试前证据，尚无测试后截图，不计算本单消耗，不拼出假对比。

S9目标3秒：1080×1920上下对比。上方为“测试前”真实截图，下方为主agent稍后取得的“测试后”真实截图；每幅只裁菜单积分区域，建议初始裁切源矩形x=74,y=394,w=300,h=98，导出前以实际裁切复核文字完整。按宽972缩放并在1080画布居中，留标签、真实余额和真实差额位置；不展示账号头像/昵称与购买按钮可进一步缩窄到余额区域（例如x=226,y=399,w=133,h=56），但须保留“积分余额”标签。测试前后若布局变化，分别独立选框，不能机械套同坐标。

版本证据原截图单独保留；S9无需在3秒内兼顾版本号。只有后截图取得、时间与同一账号/任务核准后才填写消耗=511.2−实际后余额。若任务后余额无法取得，S9只用单张标“测试前511.2，测试后未取得”，明确缺口，不能编对比。

## 交付边界

本轮未输出粗剪成片、未操作UI、未安装工具、未删除文件。可执行方案待主agent取得实际测试后材料。原素材保持未修改。

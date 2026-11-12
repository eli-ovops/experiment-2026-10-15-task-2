import CoreGraphics
import Foundation
let opts: CGWindowListOption = [.optionAll, .excludeDesktopElements]
let info = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] ?? []
let onlyTestApp = info.filter {
 let owner = $0[kCGWindowOwnerName as String] as? String ?? ""
 let name = $0[kCGWindowName as String] as? String ?? ""
 return owner.contains("WorkBuddy") || ((owner == "Finder" || owner == "访达") && name.contains("周报测试"))
}
let displays = (0..<4).map { i -> [String:Any] in
  var ids = [CGDirectDisplayID](repeating: 0, count: 8)
  var n: UInt32 = 0
  CGGetActiveDisplayList(8, &ids, &n)
  guard i < Int(n) else { return [:] }
  let id=ids[i]; let r=CGDisplayBounds(id)
  return ["index":i+1,"id":id,"x":r.origin.x,"y":r.origin.y,"width":r.width,"height":r.height]
}.filter { !$0.isEmpty }
let output: [String:Any] = ["workbuddy_windows": onlyTestApp, "displays":displays]
let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted,.sortedKeys])
print(String(data:data,encoding:.utf8)!)

using NUnit.Framework;
using UnityEngine;

namespace Naris.Tests {
public class PlatformProfileTests {
 [Test] public void DesktopProfileSupportsKeyboardMouseAndGamepad() {
  var p=PlatformProfile.For(RuntimePlatform.WindowsPlayer);
  Assert.IsTrue(p.KeyboardMouse); Assert.IsTrue(p.Gamepad); Assert.IsFalse(p.Touch);
 }
 [Test] public void MobileProfileEnablesTouchAndCapsQuality() {
  var p=PlatformProfile.For(RuntimePlatform.Android);
  Assert.IsTrue(p.Touch); Assert.LessOrEqual(p.MaxQuality,2);
 }
 [Test] public void InputFrameNormalizesMovement() {
  var f=new InputFrame(2,2,0,0,false,false,false,false,false,false);
  Assert.LessOrEqual(f.Move.sqrMagnitude,1.001f);
 }
}
}

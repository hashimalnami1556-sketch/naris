using System;
using System.Collections;
using System.IO;
using UnityEngine;
namespace Naris {
public sealed class RuntimeSmokeTest : MonoBehaviour {
    public WorldBootstrap world;
    IEnumerator Start() {
        yield return new WaitForSeconds(.5f);
        string savePath=SaveStore.PathName;
        byte[] previous=File.Exists(savePath)?File.ReadAllBytes(savePath):null;
        try {
            Check(world.Player != null,"player spawn");
            Check(world.Player.GetComponent<ActorVisual>() != null,"player model attached");
            foreach(var actor in FindObjectsByType<ActorVisual>(FindObjectsSortMode.None)) {
                var animation=actor.GetComponentInChildren<Animation>();
                Check(animation != null && animation.GetClipCount()>0,"model animation clips");
            }
            Check(Resources.Load<AudioClip>("Audio/chime_01") != null,"pickup audio");
            Check(FindObjectsByType<EnemyBrain>(FindObjectsSortMode.None).Length==3,"enemy spawns");
            var health=world.Player.GetComponent<Health>();
            health.Damage(25); Check(Mathf.Approximately(health.Current,75),"damage");
            health.Restore(100); Check(!health.Dead,"restore");
            var enemy=FindFirstObjectByType<EnemyBrain>();
            enemy.GetComponent<Health>().Damage(1000); Check(!enemy.gameObject.activeSelf,"enemy death");
            SaveStore.Write(5); Check(SaveStore.Read()==5,"nonsequential ember save");
            world.Load(); Check(world.Shards==2,"restore ember mask");
            var cc=world.Player.GetComponent<CharacterController>();
            var before=world.Player.transform.position;
            cc.Move(Vector3.forward); Check(world.Player.transform.position.z>before.z+.5f,"movement");
            Debug.Log("NARIS_SMOKE_PASS: spawn, damage, death, save/load, movement");
        } catch(Exception e) { Debug.LogException(e); Application.Quit(1); yield break; }
        finally {
            if(previous!=null) File.WriteAllBytes(savePath,previous);
            else if(File.Exists(savePath)) File.Delete(savePath);
        }
        yield return new WaitForSeconds(.2f);
        Application.Quit(0);
    }
    static void Check(bool condition,string name) {
        if(!condition) throw new Exception("NARIS_SMOKE_FAIL: "+name);
        Debug.Log("NARIS_CHECK_PASS: "+name);
    }
}
}

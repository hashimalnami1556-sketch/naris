using UnityEngine;
namespace Naris {
public sealed class WorldBootstrap : MonoBehaviour {
    public Material stone, ember, teal, ground;
    public PlayerMotor Player { get; private set; }
    public int Shards { get; private set; }
    public bool Won { get; private set; }
    bool started;
    string message = "Recover three embers, then return to the gate.";
    readonly Vector3[] relics = {new Vector3(-12,1,12),new Vector3(12,1,18),new Vector3(0,1,30)};
    readonly GameObject[] pickups = new GameObject[3];
    void Start() {
        PlatformBootstrap.ApplyCurrent();
        Time.timeScale = 0;
        gameObject.AddComponent<NarisAudio>();
        gameObject.AddComponent<AshEnvironment>();
        RenderSettings.fog = true; RenderSettings.fogColor = new Color(.065f,.08f,.10f);
        RenderSettings.fogDensity = .014f; RenderSettings.ambientLight = new Color(.32f,.37f,.42f);
        Block("Ash Court",new Vector3(0,-.5f,12),new Vector3(40,1,50),ground);
        Block("West wall",new Vector3(-20,2,12),new Vector3(1,5,50),stone);
        Block("East wall",new Vector3(20,2,12),new Vector3(1,5,50),stone);
        Block("North wall",new Vector3(0,2,37),new Vector3(40,5,1),stone);
        Block("South wall",new Vector3(0,2,-13),new Vector3(40,5,1),stone);
        for(int i=0;i<8;i++) {
            float z = i*6-8;
            Block("West ruin",new Vector3(-17,2,z),new Vector3(2,4,2),stone);
            Block("East ruin",new Vector3(17,2,z),new Vector3(2,4,2),stone);
        }
        Block("Gate left",new Vector3(-3,3,-7),new Vector3(1,6,1),stone);
        Block("Gate right",new Vector3(3,3,-7),new Vector3(1,6,1),stone);
        Block("Gate crown",new Vector3(0,6,-7),new Vector3(7,1,1),ember);
        var sun = new GameObject("Dusk light").AddComponent<Light>();
        sun.type = LightType.Directional; sun.intensity = 1.2f; sun.transform.rotation = Quaternion.Euler(35,-30,0);
        var player = Actor("Ashen Vessel",new Vector3(0,1,-3),teal,"SK_AshenVessel",1.8f);
        Player = player.AddComponent<PlayerMotor>();
        var camera = new GameObject("Main Camera").AddComponent<Camera>();
        camera.tag = "MainCamera"; camera.farClipPlane = 140;
        camera.backgroundColor = RenderSettings.fogColor; camera.clearFlags = CameraClearFlags.SolidColor;
        camera.gameObject.AddComponent<AudioListener>(); Player.view = camera.transform;
        for(int i=0;i<relics.Length;i++) {
            pickups[i] = Block("Ember "+(i+1),relics[i],Vector3.one*.65f,ember);
            Destroy(pickups[i].GetComponent<Collider>());
            var glow = pickups[i].AddComponent<Light>(); glow.color = new Color(1,.35f,.05f); glow.range = 6; glow.intensity = 3;
            var enemy = Actor("Ash guard "+(i+1),relics[i]+new Vector3(0,0,-4),stone,i==1?"SK_BoneBeast":"SK_CelestialWolf",i==1?2.1f:1.1f);
            enemy.AddComponent<EnemyBrain>().target = Player;
        }
        if(System.Array.IndexOf(System.Environment.GetCommandLineArgs(),"-narisSmokeTest") >= 0) {
            Begin(); gameObject.AddComponent<RuntimeSmokeTest>().world = this;
        }
    }
    GameObject Actor(string name,Vector3 position,Material material,string model,float height) {
        var actor = new GameObject(name); actor.transform.position = position;
        var controller = actor.AddComponent<CharacterController>(); controller.height=height; controller.center=Vector3.up*(height*.5f); controller.radius=Mathf.Min(.4f,height*.35f);
        actor.AddComponent<Health>();
        if(ActorVisual.Attach(actor,model,height)) return actor;
        var body = GameObject.CreatePrimitive(PrimitiveType.Capsule); body.name="Missing model fallback";
        body.transform.SetParent(actor.transform,false); body.transform.localPosition=Vector3.up;
        body.GetComponent<Renderer>().sharedMaterial=material; Destroy(body.GetComponent<Collider>());
        return actor;
    }
    GameObject Block(string name,Vector3 position,Vector3 size,Material material) {
        var obj=GameObject.CreatePrimitive(PrimitiveType.Cube); obj.name=name;
        obj.transform.position=position; obj.transform.localScale=size;
        obj.GetComponent<Renderer>().sharedMaterial=material; return obj;
    }
    public void Begin() { NarisAudio.Play("click_01"); started=true; Time.timeScale=1; Cursor.lockState=CursorLockMode.Locked; Cursor.visible=false; }
    void Update() {
        if(!Player || !started) return;
        var input=NarisInput.Read();
        if(input.Pause && !Won && !Player.GetComponent<Health>().Dead) {
            Time.timeScale = Time.timeScale == 0 ? 1 : 0;
            Cursor.lockState = Time.timeScale == 0 ? CursorLockMode.None : CursorLockMode.Locked; Cursor.visible=Time.timeScale==0;
        }
        if(Time.timeScale==0) return;
        for(int i=0;i<pickups.Length;i++) {
            if(!pickups[i].activeSelf) continue;
            pickups[i].transform.Rotate(0,60*Time.deltaTime,0);
            if(Vector3.Distance(Player.transform.position+Vector3.up,relics[i])<2) {
                pickups[i].SetActive(false); Shards++; message="Ember recovered."; NarisAudio.Play("chime_01");
            }
        }
        if(input.Save) Save();
        if(input.Load) Load();
        if(Shards==3 && Vector3.Distance(Player.transform.position,new Vector3(0,1,-7))<3) { Won=true; NarisAudio.Play("rumble_01"); }
        if(Won || Player.GetComponent<Health>().Dead) { Time.timeScale=0; Cursor.lockState=CursorLockMode.None; Cursor.visible=true; }
    }
    public void Save() {
        try { SaveStore.Write(ShardMask()); message="Ember progress saved. Load returns you to the gate."; }
        catch(System.Exception e) { message="Save failed: "+e.Message; Debug.LogWarning(message); }
    }
    int ShardMask() { int mask=0; for(int i=0;i<3;i++) if(!pickups[i].activeSelf) mask|=1<<i; return mask; }
    public void Load() {
        try {
            int mask=SaveStore.Read(); Shards=0;
            for(int i=0;i<3;i++) { bool collected=(mask & (1<<i))!=0; pickups[i].SetActive(!collected); if(collected) Shards++; }
            var cc=Player.GetComponent<CharacterController>(); cc.enabled=false; Player.transform.position=new Vector3(0,1,-3); cc.enabled=true;
            Player.GetComponent<Health>().Restore(100); Won=false; message="Progress loaded.";
        } catch(System.Exception e) { message="Load failed: "+e.Message; Debug.LogWarning(message); }
    }
    void OnGUI() {
        if(!Player) return;
        GUI.Box(new Rect(16,16,460,112),"NARIS | ASH GATE - PLAYABLE PROTOTYPE");
        GUI.Label(new Rect(30,43,430,24),$"Health {Player.GetComponent<Health>().Current:0}   Stamina {Player.Stamina:0}   Embers {Shards}/3");
        GUI.Label(new Rect(30,68,430,24),"WASD/Gamepad move | Mouse/Gamepad attack | Sprint | Dodge");
        GUI.Label(new Rect(30,92,430,24),"Esc/Menu pause | F5 save | F9 load");
        GUI.Label(new Rect(20,Screen.height-35,800,25),message);
        if(!started || Time.timeScale==0) {
            var rect=new Rect(Screen.width/2-180,Screen.height/2-140,360,280);
            GUI.Box(rect,Won?"GATE RESTORED":Player.GetComponent<Health>().Dead?"THE ASH CLAIMED YOU":"NARIS - ASH GATE");
            if(!Won && !Player.GetComponent<Health>().Dead && GUI.Button(new Rect(rect.x+50,rect.y+50,260,35),started?"Resume":"Enter the Ash Gate")) Begin();
            if(GUI.Button(new Rect(rect.x+50,rect.y+95,260,35),"Restart expedition")) {
                Time.timeScale=1; UnityEngine.SceneManagement.SceneManager.LoadScene(0);
            }
            if(GUI.Button(new Rect(rect.x+50,rect.y+140,260,35),"Quit")) Application.Quit();
            if(System.IO.File.Exists(SaveStore.PathName) && GUI.Button(new Rect(rect.x+50,rect.y+185,260,35),"Load ember progress")) { Load(); Begin(); }
            if(started && !Player.GetComponent<Health>().Dead && GUI.Button(new Rect(rect.x+50,rect.y+230,260,35),"Save ember progress")) Save();
        }
    }
    void OnDestroy() { Time.timeScale=1; Cursor.lockState=CursorLockMode.None; Cursor.visible=true; }
}
}

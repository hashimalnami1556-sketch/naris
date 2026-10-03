using System;
using System.IO;
using UnityEngine;
namespace Naris {
[Serializable] public sealed class SaveData {
    public int version = 1;
    public int shards;
}
public static class SaveStore {
    public static string PathName => Path.Combine(Application.persistentDataPath, (Array.IndexOf(Environment.GetCommandLineArgs(), "-narisSmokeTest") >= 0 ? "naris-smoketest.json" : "naris-progress.json"));
    public static void Write(int shards) {
        string temp = PathName + ".tmp";
        File.WriteAllText(temp, JsonUtility.ToJson(new SaveData { shards = Mathf.Clamp(shards, 0, 7) }));
        if (File.Exists(PathName)) File.Replace(temp, PathName, PathName + ".bak");
        else File.Move(temp, PathName);
    }
    public static int Read() {
        if (!File.Exists(PathName)) return 0;
        var data = JsonUtility.FromJson<SaveData>(File.ReadAllText(PathName));
        if (data == null || data.version != 1 || data.shards < 0 || data.shards > 7)
            throw new InvalidDataException("Unsupported or invalid save.");
        return data.shards;
    }
}
}

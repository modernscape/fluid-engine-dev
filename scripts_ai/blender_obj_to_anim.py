import bpy
import os

# --- 設定項目 ---
directory = "/Users/forest/projects/fluid-engine-dev/build/level_set_liquid_sim_output"
file_prefix = "frame_"
file_ext = ".obj"
start_frame = 0
end_frame = 99
# ----------------

# 最初のフレームをインポートしてベースメッシュにする
first_file = os.path.join(directory, f"{file_prefix}{start_frame:06d}{file_ext}")
if os.path.exists(first_file):
    bpy.ops.wm.obj_import(filepath=first_file)
    obj = bpy.context.selected_objects[0]
    obj.name = "LevelSetLiquid"
    
    # ベースのシェイプキー作成
    obj.shape_key_add(name="Basis", from_mix=False)

    # 2フレーム目以降をシェイプキーとして追加していく
    for frame in range(start_frame + 1, end_frame + 1):
        filepath = os.path.join(directory, f"{file_prefix}{frame:06d}{file_ext}")
        if os.path.exists(filepath):
            # 一時的にインポート
            bpy.ops.wm.obj_import(filepath=filepath)
            temp_obj = bpy.context.selected_objects[0]
            
            # シェイプキーとして頂点座標をコピー
            s_key = obj.shape_key_add(name=f"frame_{frame:04d}", from_mix=False)
            for i, v in enumerate(temp_obj.data.vertices):
                if i < len(s_key.data):
                    s_key.data[i].co = v.co
            
            # 一時オブジェクトを削除
            bpy.data.objects.remove(temp_obj)
            
            # キーフレームを設定
            s_key.value = 0.0
            s_key.keyframe_insert(data_path="value", frame=frame-1)
            s_key.value = 1.0
            s_key.keyframe_insert(data_path="value", frame=frame)
            s_key.value = 0.0
            s_key.keyframe_insert(data_path="value", frame=frame+1)

    print("Level Set OBJ のインポートが完了しました！")
else:
    print("最初のファイルが見つかりません:", first_file)
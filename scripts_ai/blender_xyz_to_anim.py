import bpy
import os

# --- 設定項目 ---
directory = "/Users/forest/projects/fluid-engine-dev/build/hybrid_liquid_sim_output"
file_prefix = "frame_"
file_ext = ".xyz"
start_frame = 0
end_frame = 99
# ----------------

def load_xyz(filepath):
    coords = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): 
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    coords.append((float(parts[0]), float(parts[1]), float(parts[2])))
                except ValueError:
                    continue
    return coords

# 最初のファイルをロードして初期オブジェクトを作成
first_file = os.path.join(directory, f"{file_prefix}{start_frame:06d}{file_ext}")
initial_coords = load_xyz(first_file)

mesh = bpy.data.meshes.new(name="FluidMesh")
mesh.from_pydata(initial_coords, [], [])
mesh.update()

obj = bpy.data.objects.new("FluidParticles", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# 基準となるBasisシェイプキー
obj.shape_key_add(name="Basis", from_mix=False)

# フレームごとにシェイプキーを作成しアニメーション
for frame in range(start_frame, end_frame + 1):
    filepath = os.path.join(directory, f"{file_prefix}{frame:06d}{file_ext}")
    if os.path.exists(filepath):
        coords = load_xyz(filepath)
        
        # 頂点数が一致しているか確認
        if len(coords) == len(mesh.vertices):
            s_key = obj.shape_key_add(name=f"frame_{frame:04d}", from_mix=False)
            
            # 各シェイプキーに座標を代入
            for i, co in enumerate(coords):
                s_key.data[i].co = co
            
            # アニメーション設定（そのフレームだけ値を1.0にする）
            s_key.value = 0.0
            s_key.keyframe_insert(data_path="value", frame=frame-1)
            s_key.value = 1.0
            s_key.keyframe_insert(data_path="value", frame=frame)
            s_key.value = 0.0
            s_key.keyframe_insert(data_path="value", frame=frame+1)

print("インポート完了。タイムラインを再生してください。")
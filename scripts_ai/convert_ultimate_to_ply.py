import os
import glob
import re
import numpy as np

def convert_ultimate(base_input_dir, base_output_dir):
    for root, dirs, files in os.walk(base_input_dir):
        npy_files = [f for f in files if f.endswith('.npy')]
        if not npy_files:
            continue
            
        rel_path = os.path.relpath(root, base_input_dir)
        output_dir = os.path.join(base_output_dir, rel_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. まず、ファイル名から「グループ（フレームや名前）」ごとに分類する
        # 例: data.#point2,0000,x.npy と y.npy は同じグループとしてまとめる
        groups = {}
        
        for f in npy_files:
            file_path = os.path.join(root, f)
            
            # パターンA: #point または #line のように軸（x, y, z）が分かれているもの
            match_axis = re.search(r'#(point|line)([23]),(\d+),([xyz])', f)
            if match_axis:
                kind, dim, frame, axis = match_axis.groups()
                key = (f"{kind}{dim}", frame)
                if key not in groups:
                    groups[key] = {'type': 'axis_split', 'dim': int(dim), 'axes': {}}
                groups[key]['axes'][axis] = file_path
                continue
                
            # パターンB: #grid や data0.npy, valid0.npy, orig_#grid2,iso.npy などの1ファイル完結型
            groups[f] = {'type': 'single', 'path': file_path}

        count = 0
        
        # 2. グループごとに適切な処理を行ってPLYを出力する
        for key, info in groups.items():
            vertices = []
            output_name = ""
            
            if info['type'] == 'axis_split':
                # 【分かれているファイルを1つに統合するケース (#point / #line)】
                kind_dim, frame = key
                axes = info['axes']
                dim = info['dim']
                
                required = ['x', 'y'] if dim == 2 else ['x', 'y', 'z']
                if not all(ax in axes for ax in required):
                    continue
                    
                x = np.load(axes['x'])
                y = np.load(axes['y'])
                z = np.load(axes['z']) if dim == 3 else np.zeros_like(x)
                
                for i in range(len(x)):
                    vertices.append((float(x[i]), float(y[i]), float(z[i])))
                    
                output_name = f"{kind_dim}_{frame}.ply"
                
            elif info['type'] == 'single':
                # 【もともと1ファイルのケース (#grid, data0, valid0 など)】
                f_name = key
                file_path = info['path']
                try:
                    data = np.load(file_path)
                except Exception:
                    continue
                    
                if data.ndim == 2:
                    rows, cols = data.shape
                    for r in range(rows):
                        for c in range(cols):
                            val = float(data[r, c])
                            if np.isnan(val): continue
                            vertices.append((float(c), float(rows - r - 1), val))
                elif data.ndim == 1:
                    for i in range(len(data)):
                        val = float(data[i])
                        if np.isnan(val): continue
                        vertices.append((float(i), 0.0, val))
                else:
                    continue
                    
                base_name = os.path.splitext(f_name)[0]
                output_name = base_name.replace(',', '_').replace('#', '') + ".ply"

            if not vertices:
                continue
                
            # PLYファイルとして書き出し
            ply_path = os.path.join(output_dir, output_name)
            num_vertices = len(vertices)
            
            with open(ply_path, 'w') as pf:
                pf.write("ply\n")
                pf.write("format ascii 1.0\n")
                pf.write(f"element vertex {num_vertices}\n")
                pf.write("property float x\n")
                pf.write("property float y\n")
                pf.write("property float z\n")
                pf.write("end_header\n")
                for v in vertices:
                    pf.write(f"{v[0]} {v[1]} {v[2]}\n")
                    
            count += 1
            
        if count > 0:
            print(f"Processed: {rel_path} ({count} files)")

    print(f"\nすべての変換が完了しました！出力先: {base_output_dir}")

if __name__ == "__main__":
    input_base = "./build/manual_tests_output"
    output_base = "./ply_ultimate_output"
    
    if not os.path.exists(input_base):
        print(f"エラー: 入力フォルダが見つかりません -> {input_base}")
    else:
        convert_ultimate(input_base, output_base)
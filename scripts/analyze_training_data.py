"""
PHM 2012 訓練數據分析腳本
分析、分類並視覺化訓練數據集
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 數據集路徑
DATASET_PATH = "phm-ieee-2012-data-challenge-dataset/Learning_set"

# 根據 TRAINING.MD 的操作條件映射
OPERATING_CONDITIONS = {
    'Bearing1_1': {'condition': 1, 'load': 4000, 'speed': 1800},
    'Bearing1_2': {'condition': 1, 'load': 4200, 'speed': 1650},
    'Bearing2_1': {'condition': 2, 'load': 4200, 'speed': 1650},
    'Bearing2_2': {'condition': 2, 'load': 4000, 'speed': 1800},
    'Bearing3_1': {'condition': 3, 'load': 5000, 'speed': 1500},
    'Bearing3_2': {'condition': 3, 'load': 4200, 'speed': 1650},
}

# 實際 RUL 值 (從 TRAINING.MD)
ACTUAL_RUL = {
    'Bearing1_1': 28020,
    'Bearing1_2': 8700,
    'Bearing2_1': 9100,
    'Bearing2_2': 7960,
    'Bearing3_1': 5730,
    'Bearing3_2': 16430,
}

def analyze_bearing_data(bearing_name, bearing_path):
    """分析單個軸承的數據"""
    csv_files = sorted([f for f in os.listdir(bearing_path) if f.endswith('.csv')])

    if not csv_files:
        return None

    # 讀取第一個文件以了解數據格式
    first_file = os.path.join(bearing_path, csv_files[0])
    df_sample = pd.read_csv(first_file, header=None)

    # 數據格式: hour, minute, second, microsecond, horiz_vibration, vert_vibration
    # (根據觀察到的格式)

    analysis = {
        'bearing_name': bearing_name,
        'condition': OPERATING_CONDITIONS[bearing_name]['condition'],
        'load_N': OPERATING_CONDITIONS[bearing_name]['load'],
        'speed_rpm': OPERATING_CONDITIONS[bearing_name]['speed'],
        'actual_RUL_min': ACTUAL_RUL[bearing_name],
        'num_files': len(csv_files),
        'data_points_per_file': len(df_sample),
        'sampling_rate_hz': 25600,  # 根據 TRAINING.MD
        'duration_per_file_sec': len(df_sample) / 25600,
        'total_duration_sec': (len(csv_files) * len(df_sample)) / 25600,
        'total_duration_min': (len(csv_files) * len(df_sample)) / 25600 / 60,
    }

    # 計算一些基本統計
    vibration_stats = []
    sample_indices = np.linspace(0, len(csv_files)-1, min(50, len(csv_files)), dtype=int)

    for idx in sample_indices:
        file_path = os.path.join(bearing_path, csv_files[idx])
        df = pd.read_csv(file_path, header=None)

        horiz_vib = df.iloc[:, 4].values  # 水平振動
        vert_vib = df.iloc[:, 5].values   # 垂直振動

        vibration_stats.append({
            'file_index': idx,
            'time_min': idx * 10,  # 每10分鐘一個文件
            'horiz_rms': np.sqrt(np.mean(horiz_vib**2)),
            'vert_rms': np.sqrt(np.mean(vert_vib**2)),
            'horiz_peak': np.max(np.abs(horiz_vib)),
            'vert_peak': np.max(np.abs(vert_vib)),
            'horiz_kurtosis': pd.Series(horiz_vib).kurtosis(),
            'vert_kurtosis': pd.Series(vert_vib).kurtosis(),
        })

    analysis['vibration_stats'] = pd.DataFrame(vibration_stats)

    return analysis

def create_summary_table(all_analyses):
    """創建數據摘要表格"""
    summary_data = []

    for analysis in all_analyses:
        summary_data.append({
            '軸承編號': analysis['bearing_name'],
            '操作條件': f"Condition {analysis['condition']}",
            '負載 (N)': analysis['load_N'],
            '轉速 (RPM)': analysis['speed_rpm'],
            '實際 RUL (分鐘)': analysis['actual_RUL_min'],
            '數據文件數': analysis['num_files'],
            '總時長 (分鐘)': f"{analysis['total_duration_min']:.1f}",
            '每文件數據點': analysis['data_points_per_file'],
            '採樣率 (Hz)': analysis['sampling_rate_hz'],
        })

    df_summary = pd.DataFrame(summary_data)
    return df_summary

def plot_data_overview(all_analyses, output_dir):
    """繪製數據概覽圖表"""

    # 1. 各軸承的數據量對比
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    bearing_names = [a['bearing_name'] for a in all_analyses]
    num_files = [a['num_files'] for a in all_analyses]
    rul_values = [a['actual_RUL_min'] for a in all_analyses]
    conditions = [f"Cond {a['condition']}" for a in all_analyses]

    # 子圖1: 數據文件數量
    ax = axes[0, 0]
    colors = ['#1f77b4' if c == 'Cond 1' else '#ff7f0e' if c == 'Cond 2' else '#2ca02c'
              for c in conditions]
    bars = ax.bar(bearing_names, num_files, color=colors)
    ax.set_title('Number of Data Files per Bearing', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bearing ID')
    ax.set_ylabel('Number of Files')
    ax.grid(axis='y', alpha=0.3)

    # 添加數值標籤
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')

    # 子圖2: 實際 RUL 值
    ax = axes[0, 1]
    bars = ax.bar(bearing_names, rul_values, color=colors)
    ax.set_title('Actual Remaining Useful Life (RUL)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Bearing ID')
    ax.set_ylabel('RUL (minutes)')
    ax.grid(axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')

    # 子圖3: 操作條件分布
    ax = axes[1, 0]
    condition_counts = pd.Series(conditions).value_counts().sort_index()
    ax.pie(condition_counts.values, labels=condition_counts.index, autopct='%1.0f%%',
           colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax.set_title('Distribution by Operating Condition', fontsize=14, fontweight='bold')

    # 子圖4: 負載 vs 轉速散點圖
    ax = axes[1, 1]
    loads = [a['load_N'] for a in all_analyses]
    speeds = [a['speed_rpm'] for a in all_analyses]

    for i, (load, speed, name, color) in enumerate(zip(loads, speeds, bearing_names, colors)):
        ax.scatter(speed, load, s=300, c=color, alpha=0.6, edgecolors='black', linewidth=2)
        ax.text(speed, load, name, ha='center', va='center', fontsize=9, fontweight='bold')

    ax.set_title('Operating Conditions: Load vs Speed', fontsize=14, fontweight='bold')
    ax.set_xlabel('Speed (RPM)')
    ax.set_ylabel('Load (N)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'data_overview.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/data_overview.png")
    plt.close()

def plot_vibration_trends(all_analyses, output_dir):
    """繪製振動趨勢圖"""

    n_bearings = len(all_analyses)
    fig, axes = plt.subplots(n_bearings, 2, figsize=(16, 4*n_bearings))

    if n_bearings == 1:
        axes = axes.reshape(1, -1)

    for idx, analysis in enumerate(all_analyses):
        stats = analysis['vibration_stats']
        bearing_name = analysis['bearing_name']
        rul = analysis['actual_RUL_min']

        # 水平振動 RMS
        ax = axes[idx, 0]
        ax.plot(stats['time_min'], stats['horiz_rms'], 'b-', linewidth=2, label='Horizontal RMS')
        ax.axvline(x=rul, color='r', linestyle='--', linewidth=2, label=f'RUL={rul} min')
        ax.set_title(f'{bearing_name} - Horizontal Vibration RMS', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('RMS Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 垂直振動 RMS
        ax = axes[idx, 1]
        ax.plot(stats['time_min'], stats['vert_rms'], 'g-', linewidth=2, label='Vertical RMS')
        ax.axvline(x=rul, color='r', linestyle='--', linewidth=2, label=f'RUL={rul} min')
        ax.set_title(f'{bearing_name} - Vertical Vibration RMS', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('RMS Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vibration_trends.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/vibration_trends.png")
    plt.close()

def plot_kurtosis_trends(all_analyses, output_dir):
    """繪製峰度趨勢圖（故障檢測指標）"""

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for idx, analysis in enumerate(all_analyses):
        stats = analysis['vibration_stats']
        bearing_name = analysis['bearing_name']
        rul = analysis['actual_RUL_min']

        ax = axes[idx]
        ax.plot(stats['time_min'], stats['horiz_kurtosis'], 'b-', linewidth=2,
                marker='o', markersize=4, label='Horizontal Kurtosis')
        ax.plot(stats['time_min'], stats['vert_kurtosis'], 'g-', linewidth=2,
                marker='s', markersize=4, label='Vertical Kurtosis')
        ax.axvline(x=rul, color='r', linestyle='--', linewidth=2, label=f'RUL={rul} min')
        ax.axhline(y=3, color='orange', linestyle=':', linewidth=1.5, label='Normal (≈3)')

        ax.set_title(f'{bearing_name} - Kurtosis Trend', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Kurtosis')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'kurtosis_trends.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/kurtosis_trends.png")
    plt.close()

def main():
    """主函數"""
    print("=" * 80)
    print("PHM 2012 訓練數據分析")
    print("=" * 80)

    # 創建輸出目錄
    output_dir = "phm_analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    # 分析所有軸承
    all_analyses = []

    for bearing_name in sorted(OPERATING_CONDITIONS.keys()):
        bearing_path = os.path.join(DATASET_PATH, bearing_name)

        if not os.path.exists(bearing_path):
            print(f"Warning: {bearing_path} not found")
            continue

        print(f"\n分析 {bearing_name}...")
        analysis = analyze_bearing_data(bearing_name, bearing_path)

        if analysis:
            all_analyses.append(analysis)
            print(f"  - 文件數: {analysis['num_files']}")
            print(f"  - 總時長: {analysis['total_duration_min']:.1f} 分鐘")
            print(f"  - 實際 RUL: {analysis['actual_RUL_min']} 分鐘")

    # 創建摘要表格
    print("\n" + "=" * 80)
    print("創建摘要表格...")
    df_summary = create_summary_table(all_analyses)
    print("\n訓練數據摘要:")
    print(df_summary.to_string(index=False))

    # 保存表格
    df_summary.to_csv(os.path.join(output_dir, 'training_data_summary.csv'),
                      index=False, encoding='utf-8-sig')
    print(f"\nSaved: {output_dir}/training_data_summary.csv")

    # 保存詳細分析結果
    detailed_results = []
    for analysis in all_analyses:
        stats_df = analysis['vibration_stats']
        stats_df['bearing_name'] = analysis['bearing_name']
        detailed_results.append(stats_df)

    df_detailed = pd.concat(detailed_results, ignore_index=True)
    df_detailed.to_csv(os.path.join(output_dir, 'vibration_statistics.csv'),
                       index=False, encoding='utf-8-sig')
    print(f"Saved: {output_dir}/vibration_statistics.csv")

    # 繪製圖表
    print("\n" + "=" * 80)
    print("繪製圖表...")
    plot_data_overview(all_analyses, output_dir)
    plot_vibration_trends(all_analyses, output_dir)
    plot_kurtosis_trends(all_analyses, output_dir)

    # 生成 JSON 摘要
    summary_json = {
        'dataset': 'PHM IEEE 2012 Challenge - Learning Set',
        'total_bearings': len(all_analyses),
        'operating_conditions': 3,
        'bearings': []
    }

    for analysis in all_analyses:
        summary_json['bearings'].append({
            'name': analysis['bearing_name'],
            'condition': analysis['condition'],
            'load_N': analysis['load_N'],
            'speed_rpm': analysis['speed_rpm'],
            'actual_RUL_min': analysis['actual_RUL_min'],
            'num_files': analysis['num_files'],
            'total_duration_min': round(analysis['total_duration_min'], 2),
        })

    with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)
    print(f"Saved: {output_dir}/summary.json")

    print("\n" + "=" * 80)
    print("分析完成！")
    print(f"所有結果保存在: {output_dir}/")
    print("=" * 80)

if __name__ == "__main__":
    main()

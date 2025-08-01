#!/usr/bin/env python3
"""
한글 폰트 문제를 해결하는 스크립트
"""

import subprocess
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys

def install_nanum_fonts():
    """
    나눔 폰트를 설치하는 함수 (Linux용)
    """
    try:
        print("나눔 폰트 설치를 시도합니다...")
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'fonts-nanum*'], check=True)
        print("나눔 폰트 설치가 완료되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"폰트 설치 중 오류가 발생했습니다: {e}")
        return False

def clear_matplotlib_cache():
    """
    matplotlib 폰트 캐시를 삭제하고 재구성
    """
    try:
        cache_dir = fm.get_cachedir()
        print(f"matplotlib 캐시 디렉토리: {cache_dir}")
        
        # 캐시 파일들 삭제
        import glob
        cache_files = glob.glob(os.path.join(cache_dir, "*.cache"))
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
                print(f"삭제됨: {cache_file}")
            except:
                pass
        
        # 폰트 리스트 재구성
        fm._rebuild()
        print("matplotlib 폰트 캐시가 재구성되었습니다.")
        return True
    except Exception as e:
        print(f"캐시 삭제 중 오류: {e}")
        return False

def test_korean_font():
    """
    한글 폰트가 제대로 작동하는지 테스트
    """
    try:
        import matplotlib.pyplot as plt
        
        # 사용 가능한 나눔 폰트 찾기
        available_fonts = []
        for font in fm.fontManager.ttflist:
            if 'nanum' in font.name.lower():
                available_fonts.append(font.name)
        
        if not available_fonts:
            print("나눔 폰트를 찾을 수 없습니다.")
            return False
        
        # 첫 번째 나눔 폰트 사용
        font_name = available_fonts[0]
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False
        
        # 테스트 그래프 생성
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title('한글 폰트 테스트 - 삼성전자 주가 분석')
        ax.set_xlabel('날짜')
        ax.set_ylabel('가격 (원)')
        
        # 테스트 이미지 저장
        plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"한글 폰트 테스트 완료: {font_name}")
        print("테스트 이미지가 'font_test.png'로 저장되었습니다.")
        return True
        
    except Exception as e:
        print(f"폰트 테스트 중 오류: {e}")
        return False

def fix_font_issues():
    """
    폰트 문제를 종합적으로 해결
    """
    print("=== 한글 폰트 문제 해결 시작 ===")
    
    # 1. 현재 사용 가능한 폰트 확인
    print("\n1. 현재 사용 가능한 한글 폰트:")
    korean_fonts = []
    for font in fm.fontManager.ttflist:
        if any(keyword in font.name.lower() for keyword in ['nanum', 'gothic', 'myeongjo']):
            korean_fonts.append(font.name)
    
    if korean_fonts:
        for font in sorted(set(korean_fonts)):
            print(f"  - {font}")
    else:
        print("  한글 폰트가 발견되지 않았습니다.")
    
    # 2. matplotlib 캐시 정리
    print("\n2. matplotlib 캐시 정리...")
    clear_matplotlib_cache()
    
    # 3. 폰트 테스트
    print("\n3. 한글 폰트 테스트...")
    if test_korean_font():
        print("✅ 한글 폰트가 정상적으로 작동합니다.")
    else:
        print("❌ 한글 폰트 테스트에 실패했습니다.")
        
        # Linux인 경우 폰트 설치 시도
        import platform
        if platform.system() == 'Linux':
            print("\n4. 나눔 폰트 설치 시도...")
            if install_nanum_fonts():
                clear_matplotlib_cache()
                if test_korean_font():
                    print("✅ 폰트 설치 후 한글 폰트가 정상 작동합니다.")
                else:
                    print("❌ 폰트 설치 후에도 문제가 지속됩니다.")
    
    print("\n=== 폰트 문제 해결 완료 ===")

if __name__ == "__main__":
    fix_font_issues()

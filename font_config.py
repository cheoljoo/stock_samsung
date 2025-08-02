import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import warnings

def setup_korean_font_robust():
    """
    더 안정적인 한글 폰트 설정 함수
    """
    # 경고 메시지 억제
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    
    # 사용 가능한 모든 폰트 목록 가져오기
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 한글 폰트 우선순위 목록
    korean_font_candidates = [
        'NanumGothic',
        'NanumBarunGothic', 
        'NanumMyeongjo',
        'Nanum Gothic',
        'DejaVu Sans'
    ]
    
    selected_font = None
    
    # 사용 가능한 한글 폰트 찾기
    for font_candidate in korean_font_candidates:
        if font_candidate in available_fonts:
            selected_font = font_candidate
            break
        # 대소문자 구분 없이 검색
        for available_font in available_fonts:
            if font_candidate.lower() in available_font.lower():
                selected_font = available_font
                break
        if selected_font:
            break
    
    # 폰트 설정
    if selected_font:
        plt.rcParams['font.family'] = selected_font
        print(f"한글 폰트 설정: {selected_font}")
    else:
        # 대안: sans-serif 사용하고 한글이 있는 폰트 찾기
        plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
        print("기본 폰트를 사용합니다. 한글이 깨질 수 있습니다.")
    
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    
    return selected_font is not None

def setup_korean_font():
    """
    기존 함수와의 호환성을 위한 래퍼 함수
    """
    return setup_korean_font_robust()

def get_available_korean_fonts():
    """
    시스템에서 사용 가능한 한글 폰트 목록을 반환
    """
    korean_font_keywords = ['nanum', 'malgun', 'apple', 'gothic', 'myeongjo']
    available_fonts = []
    
    for font in fm.fontManager.ttflist:
        font_name = font.name.lower()
        if any(keyword in font_name for keyword in korean_font_keywords):
            available_fonts.append(font.name)
    
    return sorted(set(available_fonts))

# 모듈 import시 자동으로 폰트 설정
setup_korean_font_robust()

if __name__ == "__main__":
    print("=== 한글 폰트 테스트 ===")
    print(f"현재 설정된 폰트: {plt.rcParams['font.family']}")
    
    # 사용 가능한 모든 폰트 출력
    available_fonts = sorted([f.name for f in fm.fontManager.ttflist])
    print(f"\n시스템에 설치된 총 폰트 수: {len(available_fonts)}")
    
    # 한글 관련 폰트만 필터링
    korean_fonts = [font for font in available_fonts if any(keyword in font.lower() for keyword in ['nanum', 'gothic', 'myeongjo', 'korean'])]
    if korean_fonts:
        print("\n한글 관련 폰트:")
        for font in korean_fonts:
            print(f"  - {font}")
    else:
        print("\n한글 관련 폰트를 찾을 수 없습니다.")

import os
from PIL import Image
from PIL.ExifTags import TAGS

def get_positive_prompt_from_image(image_path):
    """
    단일 이미지 파일에서 Stable Diffusion 긍정 프롬프트를 추출합니다.
    PNG와 JPG/JPEG 형식을 모두 지원합니다.

    Args:
        image_path (str): 이미지 파일의 경로

    Returns:
        str: 추출된 긍정 프롬프트 문자열. 없으면 None.
    """
    try:
        img = Image.open(image_path)
        raw_info = ""

        # PNG 파일의 메타데이터 (PNG info) 처리
        if image_path.lower().endswith('.png'):
            # 'parameters' 키에 생성 정보가 저장되어 있는 경우가 많음
            raw_info = img.info.get('parameters', '')
        
        # JPEG 파일의 메타데이터 (EXIF) 처리
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            exif_data = img._getexif()
            if exif_data:
                # UserComment 태그(0x9286)에 생성 정보가 저장되는 경우가 많음
                user_comment_tag = 0x9286
                if user_comment_tag in exif_data:
                    # bytes를 utf-8로 디코딩
                    raw_info = exif_data[user_comment_tag].decode('utf-8', errors='ignore')

        if not raw_info:
            return None

        # "Negative prompt:" 앞부분을 긍정 프롬프트로 간주
        neg_prompt_marker = "Negative prompt:"
        if neg_prompt_marker in raw_info:
            positive_prompt = raw_info.split(neg_prompt_marker)[0]
        else:
            # Negative prompt가 없는 경우, "Steps:" 이전까지를 프롬프트로 간주
            steps_marker = "Steps:"
            if steps_marker in raw_info:
                positive_prompt = raw_info.split(steps_marker)[0]
            else:
                positive_prompt = raw_info

        # 앞뒤 공백 및 줄바꿈 제거 후 반환
        return positive_prompt.strip()

    except Exception as e:
        print(f"오류 발생 ({os.path.basename(image_path)}): {e}")
        return None

def main():
    """
    메인 실행 함수
    """
    # 사용자로부터 폴더 경로 입력받기
    folder_path = input("이미지 프롬프트를 추출할 폴더 경로를 입력하세요: ")

    if not os.path.isdir(folder_path):
        print(f"오류: '{folder_path}'는 유효한 폴더가 아닙니다.")
        return

    print(f"\n[{folder_path}] 폴더의 이미지들을 스캔합니다...")
    print("-" * 50)

    # 지원하는 이미지 확장자
    supported_extensions = ('.png', '.jpg', '.jpeg')

    # 폴더 내 파일 순회
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_extensions):
            full_path = os.path.join(folder_path, filename)
            
            print(f"▶️ 파일: {filename}")
            
            prompt = get_positive_prompt_from_image(full_path)
            
            if prompt:
                print(f"✅ 추출된 프롬프트:\n{prompt}\n")
            else:
                print("❌ 프롬프트를 찾을 수 없습니다.\n")
    
    print("-" * 50)
    print("모든 이미지 파일 스캔을 완료했습니다.")


if __name__ == "__main__":
    main()
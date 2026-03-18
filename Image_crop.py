import os
from PIL import Image
import cv2
import numpy as np
import Learning_conversion


class ImageLoader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = self._load_image()

    def _load_image(self):
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"画像がない: {self.image_path}")

        # 拡張子を小文字に変換してチェック
        # ARATAはアノテーションデータがGifであることが多いので、gifにも対応
        ext = os.path.splitext(self.image_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            image = cv2.imread(self.image_path)
        elif ext == '.gif':
            with Image.open(self.image_path) as img:
                frame_rgb = img.convert("RGB")
                frame_np = np.array(frame_rgb)
                image = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        else:
            raise ValueError(f"対応していない拡張子: {ext}")

        if image is None:
            raise ValueError(f"ロードの失敗: {self.image_path}")

        return image


class ImageCropper:
    """
    画像を指定されたサイズで分割するクラス
    デフォルトの分割サイズは400x400ピクセル
    分割する際に、画像の中央を基準にして余白を均等に配置するように、
    開始位置を画像サイズ//分割サイズ/2に設定
    """
    def __init__(self, image, crop_size=(400, 400)):
        self.image = image
        self.crop_width, self.crop_height = crop_size

    def crop_and_save(self, output_dir, prefix):
        os.makedirs(output_dir, exist_ok=True)

        height, width = self.image.shape[:2]
        count_x = width // self.crop_width
        count_y = height // self.crop_height
        margin_x = width % self.crop_width // 2
        margin_y = height % self.crop_height // 2
        
        

        print(f"画像サイズ: {width}x{height}")
        print(f"分割枚数: {count_x} x {count_y}")

        for i in range(count_x):
            for j in range(count_y):
                x_start = i * self.crop_width  + margin_x
                y_start = j * self.crop_height + margin_y
                x_end = x_start + self.crop_width
                y_end = y_start + self.crop_height

                cropped_image = self.image[y_start:y_end, x_start:x_end]
                output_path = os.path.join(output_dir, f"{prefix}_{i}_{j}.png")
                print(f"Saving: {output_path}")
                cv2.imwrite(output_path, cropped_image)


class FileManager:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.files = sorted([
            f for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f)) 
            and not f.startswith('.')
        ])

    def get_input_path(self, index):
        return os.path.join(self.input_dir, self.files[index])

    def get_output_prefix(self, index):
        filename = os.path.splitext(self.files[index])[0]
        return filename 

    def get_file_count(self):
        return len(self.files)
    
    def is_hidden(self,filepath):
        return os.path.basename(filepath).startswith('.')


class CropApplication:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.file_manager = FileManager(input_dir, output_dir)

    def run(self):
        total_files = self.file_manager.get_file_count()
        print(f"ファイル数 : {total_files}")

        for i in range(total_files):
            input_path = self.file_manager.get_input_path(i)
            prefix = str("image" + str(i))

            print(f"\nファイル名: {input_path}")

            try:
                image = ImageLoader(input_path).image
                cropper = ImageCropper(image)
                cropper.crop_and_save(self.output_dir, prefix)
            except Exception as e:
                print(f"Error processing {input_path}: {e}")


if __name__ == "__main__":
    input_directory = "./input"
    output_directory = "./output"
    
    

    app = CropApplication(input_directory, output_directory)
    app.run()
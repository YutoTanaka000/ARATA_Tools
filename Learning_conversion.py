import cv2
import numpy as np
import os
from PIL import Image


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


class ARATAImageEditer:
    def __init__(self, image,):
        pass 
    
    def drew_corner(self,img,  RGB=(0, 255, 0)):
        # 輪郭を入力カラー(RGB)で塗りつぶし
        
        img_copy = img.copy()
        # 画像をグレースケールに変換
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二値化
        _, binary = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        # 輪郭を検出
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # 輪郭を描画
        result = cv2.drawContours(img, contours, -1, RGB , 1)
        
        return result
    
    def color_convert(self,img, beforRGB=(255, 255, 255), afterRGB=(0, 0, 255)):
        # 色変換
        img_copy = img.copy()
        # 引数をもとに色変換
        mask = np.all(img == beforRGB, axis=-1)
        img[mask] = np.array(afterRGB)
        
        return img
    
    def root_classifying(self, img):
        coner = self.drew_corner(img)
        color_converted = self.color_convert(coner)
        return color_converted
    

class RootClassifying:
    def __init__(self, input_dir, output_dir):
        self.file_manager = FileManager(input_dir, output_dir)

    def process_images(self):
        for i in range(self.file_manager.get_file_count()):
            input_path = self.file_manager.get_input_path(i)
            output_prefix = self.file_manager.get_output_prefix(i)
            output_path = os.path.join(self.file_manager.output_dir, f"{output_prefix}.png")
            
            print(f"Processing {input_path} to {output_path}")
            img_loader = ImageLoader(input_path)
            img = img_loader.image
            
            arata_editer = ARATAImageEditer(img)
            edited_img = arata_editer.root_classifying(img)
            
            cv2.imwrite(output_path, edited_img)
            print(f"Saved edited image to {output_path}")
    
    
if __name__ == "__main__":
    input_dir = "input"    # 入力画像ディレクトリ
    output_dir = "output"  # 出力画像ディレクトリ
    
    file_manager = FileManager(input_dir, output_dir)

    # 画像処理を実行
    root_classifier = RootClassifying(input_dir, output_dir)
    root_classifier.process_images()
    
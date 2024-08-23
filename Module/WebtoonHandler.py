import aiohttp
from bs4 import BeautifulSoup
from img2pdf import convert
import os, tqdm

class WebtoonHandler:
    def __init__(self):
        self.base_url = "https://comic.naver.com/webtoon/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.webtoon_title = ""
        self.webtoon_id = 0
        self.webtoon_max_no = 0
        self.webtoon_to_down = 0

    async def fetch(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    raise Exception("웹툰을 불러오는 데 실패했습니다.")
                return await response.text()

    async def max_no(self, title_id: int):
        url = f"{self.base_url}detail?titleId={title_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        webtoon_t = soup.find("title").text.split(" ")[0]
        max_no = int(str(response.url).split("&")[1].split("=")[1])
        return max_no, webtoon_t

    async def get_image_url(self, title_id: int, webtoon_to_down) -> dict:
        self.webtoon_to_down = webtoon_to_down
        image_urls = {}

        self.webtoon_max_no, self.webtoon_title = await self.max_no(title_id)
        if self.webtoon_to_down == "전부":
            self.webtoon_to_down = self.webtoon_max_no
        else:
            self.webtoon_to_down = int(self.webtoon_to_down)

        if self.webtoon_to_down > self.webtoon_max_no:
            raise Exception("[웹툰] 해당 웹툰의 마지막화보다 큰 숫자를 입력하셨습니다.")
        self.webtoon_id = title_id

        async with aiohttp.ClientSession() as session:
            for k in range(1, self.webtoon_to_down + 1):
                url = f"{self.base_url}detail?titleId={title_id}&no={k}"
                html = await self.fetch(url)
                soup = BeautifulSoup(html, "html.parser")
                img_url = soup.select("div.wt_viewer img")
                image_urls[str(k)] = [img["src"] for img in img_url]

        return image_urls

    async def download_images(self, title_id: int, webtoon_to_down):
        image_urls = await self.get_image_url(title_id, webtoon_to_down)
        directory = f"{self.webtoon_title} - {title_id}"
        if not os.path.exists(directory):
            os.mkdir(directory)

        async with aiohttp.ClientSession() as session:
            for k, urls in image_urls.items():
                pbar = tqdm.tqdm(total=len(urls), desc=f"[웹툰] {k}화 다운로드 중")
                episode_dir = os.path.join(directory, f"{k}화")
                if not os.path.exists(episode_dir):
                    os.mkdir(episode_dir)
                for i, url in enumerate(urls):
                    img_path = os.path.join(episode_dir, f"{i + 1}.jpg")
                    async with session.get(url, headers=self.headers) as response:
                        img = await response.read()
                        with open(img_path, "wb") as f:
                            f.write(img)
                    pbar.update(1)
        return f"[웹툰] 다운로드 완료 [1화 -> {self.webtoon_to_down}화]"

    async def pdf(self):
        directory = f"{self.webtoon_title} - {self.webtoon_id}"
        if not os.path.exists(directory):
            raise Exception("이미지가 존재하지 않습니다")

        pdf_dir = os.path.join(directory, "pdf")
        if not os.path.exists(pdf_dir):
            os.mkdir(pdf_dir)

        for k in range(1, self.webtoon_to_down + 1):
            images = []
            episode_dir = os.path.join(directory, f"{k}화")

            for file in sorted(os.listdir(episode_dir)):
                if file.endswith(".jpg"):
                    images.append(os.path.join(episode_dir, file))

            if images:
                with open(os.path.join(pdf_dir, f"{k}.pdf"), "wb") as f:
                    f.write(convert(images))
                print(f"[PDF] 생성 완료 {k}화")

    async def clear(self):
        self.webtoon_id = 0
        self.webtoon_title = ""
        self.webtoon_max_no = 0
        self.webtoon_to_down = 0
        print("[웹툰] 초기화 완료")

    async def set(self, title_id: int, title_name: str, max_no: int, down_to):
        self.webtoon_id = title_id
        self.webtoon_title = title_name
        self.webtoon_max_no = max_no
        if down_to == "전부":
            self.webtoon_to_down = max_no
        else:
            self.webtoon_to_down = int(down_to)
        print(f"[웹툰] 설정 완료 {title_name} - {title_id}")

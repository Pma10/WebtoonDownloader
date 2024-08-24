from Module.WebtoonHandler import WebtoonHandler
import asyncio, os

async def handle_pdf(Handler):
    try:
        web_name, web_no, max_no = input("웹툰의 이름과 번호, 몇화까지 다운로드 했는지를 입력해주세요 (예: 웹툰명 10000 5): ").split()
        await Handler.set(int(web_no), web_name, int(max_no), int(max_no))
        await Handler.pdf()
    except ValueError:
        print("입력값이 잘못되었습니다. 숫자를 올바르게 입력해주세요.")
    except Exception as e:
        print(f"오류 발생1: {e}")

async def handle_download(Handler):
        webtoon_id = input("다운로드 할 웹툰 아이디를 입력해주세요: ")
        while True:
            webtoon_to_down = input("몇화까지 다운로드 할까요? ex) 1, 2 ...  또는 전부: ")
            if webtoon_to_down.isdigit() and int(webtoon_to_down) > 0:
                break
            elif webtoon_to_down == "전부":
                break
            else:
                print("올바른 숫자를 입력하세요")



        print(await Handler.download_images(int(webtoon_id), webtoon_to_down))

        make_to_pdf = input("PDF로 만드시겠습니까? [네/아니요]: ")
        if make_to_pdf.lower() == "네":
            await Handler.pdf()



async def main():
    while True:
            handler = WebtoonHandler()
            menu = input("사용하실 도구 이름을 입력해주세요 [다운로드/PDF] : ").strip().lower()

            if menu == "pdf":
                await handle_pdf(handler)
            elif menu == "다운로드":
                await handle_download(handler)
            else:
                print("유효하지 않은 메뉴입니다. '다운로드' 또는 'PDF' 중 하나를 선택해주세요.")


if __name__ == "__main__":
    asyncio.run(main())

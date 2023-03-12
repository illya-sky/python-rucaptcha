import os
import uuid
import base64
import shutil
from typing import Optional
from pathlib import Path

from python_rucaptcha.core.base import BaseCaptcha
from python_rucaptcha.core.enums import SaveFormatsEnm, ImageCaptchaEnm


class ImageCaptcha(BaseCaptcha):

    NO_CAPTCHA_ERR = "You did not send any file, local link or URL."

    def __init__(
        self,
        save_format: str = SaveFormatsEnm.TEMP.value,
        img_clearing: bool = True,
        img_path: str = "PythonRuCaptchaImages",
        *args,
        **kwargs,
    ):
        """
        The class is used to work with Image Captcha.

        Args:
            rucaptcha_key: User API key
            save_format: The format in which the image will be saved, or as a temporary file - 'temp',
                                 or as a regular image to a folder created by the library - 'const'.
            img_clearing: True - delete file after solution, False - don't delete file after solution
            img_path: Folder to save captcha images

        Examples:
            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_link="https://rucaptcha.com/dist/web/99581b9d446a509a0a01954438a5e36a.jpg")
            {
                'captchaSolve': 'W9H5K',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_file="src/examples/088636.png")
            {
                'captchaSolve': '088636',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

            >>> await ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).aio_captcha_handler(captcha_link="https://rucaptcha.com/dist/web/99581b9d446a509a0a01954438a5e36a.jpg")
            {
                'captchaSolve': 'W9H5K',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

            >>> await ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).aio_captcha_handler(captcha_file="src/examples/088636.png")
            {
                'captchaSolve': '088636',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

        Returns:
            Dict with full server response

        Notes:
            https://rucaptcha.com/api-rucaptcha#solving_normal_captcha
        """
        super().__init__(method=ImageCaptchaEnm.BASE64.value, *args, **kwargs)
        self.save_format = save_format
        self.img_clearing = img_clearing
        self.img_path = img_path

    def _image_const_saver(self, content: bytes, img_path: str):
        """
        Method create and save file in folder
        """
        Path(img_path).mkdir(parents=True, exist_ok=True)

        # generate image name
        self._image_name = f"im-{uuid.uuid4()}.png"

        # save image to folder
        with open(os.path.join(img_path, self._image_name), "wb") as out_image:
            out_image.write(content)

    @staticmethod
    def _local_image_captcha(captcha_file: str):
        """
        Method get local image, read it and prepare for sending to Captcha solving service
        """
        with open(captcha_file, "rb") as file:
            return file.read()

    def captcha_handler(
        self,
        captcha_link: Optional[str] = None,
        captcha_file: Optional[str] = None,
        captcha_base64: Optional[bytes] = None,
        **kwargs,
    ) -> dict:
        """
        Sync solving method

        Args:
            captcha_link: Captcha image URL
            captcha_file: Captcha image file path
            captcha_base64: Captcha image BASE64 info
            kwargs: additional params for `requests` library

        Examples:
            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_link="https://rucaptcha.com/dist/web/99581b9d446a509a0a01954438a5e36a.jpg")
            {
                'captchaSolve': 'W9H5K',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_file="src/examples/088636.png")
            {
                'captchaSolve': '088636',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

        Returns:
            Dict with full server response

        Notes:
            https://rucaptcha.com/api-rucaptcha#solving_funcaptcha_new
        """
        # if a local file link is passed
        if captcha_file:
            self.post_payload.update(
                {"body": base64.b64encode(self._local_image_captcha(captcha_file)).decode("utf-8")}
            )
        # if the file is transferred in base64 encoding
        elif captcha_base64:
            self.post_payload.update({"body": base64.b64encode(captcha_base64).decode("utf-8")})
        # if a URL is passed
        elif captcha_link:
            try:
                content = self.url_open(url=captcha_link, **kwargs).content
            except Exception as error:
                self.result.error = True
                self.result.errorBody = error
                return self.result.dict(exclude_none=True)

            # according to the value of the passed parameter, select the function to save the image
            if self.save_format == SaveFormatsEnm.CONST.value:
                self._image_const_saver(content, self.img_path)
            self.post_payload.update({"body": base64.b64encode(content).decode("utf-8")})

        else:
            # if none of the parameters are passed
            self.result.error = True
            self.result.errorBody = self.NO_CAPTCHA_ERR
            return self.result.dict()

        return self._processing_response(**kwargs)

    async def aio_captcha_handler(
        self,
        captcha_link: Optional[str] = None,
        captcha_file: Optional[str] = None,
        captcha_base64: Optional[bytes] = None,
        **kwargs,
    ) -> dict:
        """
        Async solving method

        Args:
            captcha_link: Captcha image URL
            captcha_file: Captcha image file path
            captcha_base64: Captcha image BASE64 info
            kwargs: additional params for `requests` library

        Examples:
            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_link="https://rucaptcha.com/dist/web/99581b9d446a509a0a01954438a5e36a.jpg")
            {
                'captchaSolve': 'W9H5K',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

            >>> ImageCaptcha(rucaptcha_key="aa9011f31111181111168611f1151122",
            ...             ).captcha_handler(captcha_file="src/examples/088636.png")
            {
                'captchaSolve': '088636',
                'taskId': '73043008354',
                'error': False,
                'errorBody': None
            }

        Returns:
            Dict with full server response

        Notes:
            https://rucaptcha.com/api-rucaptcha#solving_funcaptcha_new
        """
        # if a local file link is passed
        if captcha_file:
            self.post_payload.update(
                {"body": base64.b64encode(self._local_image_captcha(captcha_file)).decode("utf-8")}
            )
        # if the file is transferred in base64 encoding
        elif captcha_base64:
            self.post_payload.update({"body": base64.b64encode(captcha_base64).decode("utf-8")})
        # if a URL is passed
        elif captcha_link:
            try:
                content = await self.aio_url_read(url=captcha_link, **kwargs)
            except Exception as error:
                self.result.error = True
                self.result.errorBody = error
                return self.result.dict(exclude_none=True)

            # according to the value of the passed parameter, select the function to save the image
            if self.save_format == SaveFormatsEnm.CONST.value:
                self._image_const_saver(content, self.img_path)
            self.post_payload.update({"body": base64.b64encode(content).decode("utf-8")})

        else:
            # if none of the parameters are passed
            self.result.error = True
            self.result.errorBody = self.NO_CAPTCHA_ERR
            return self.result.dict()

        return await self._aio_processing_response()

    def __del__(self):
        if self.save_format == SaveFormatsEnm.CONST.value and self.img_clearing:
            shutil.rmtree(self.img_path)


'''
class sockNormalCaptcha(WebSocketRuCaptcha):
    """
    Class for ImageCaptcha
    """

    def __init__(self, rucaptcha_key: str, allSessions: bool = None, suppressSuccess: bool = None):
        """
        Method setup WebSocket connection data
        """
        super().__init__(allSessions, suppressSuccess)
        self.rucaptcha_key = rucaptcha_key

    async def captcha_handler(self, captcha_image_base64: str, **kwargs) -> dict:
        """
        The asynchronous WebSocket method return account balance.
        More info - https://wsrucaptcha.docs.apiary.io/#reference/text-captcha
        :param captcha_image_base64: Image captcha base64 data in string format (decoded in utf-8)
        :param kwargs: Options variables
        :return: Server response dict
        """
        normal_captcha_payload = NormalCaptchaSocketSer(
            **{
                "method": "normal",
                "requestId": str(uuid4()),
                "body": captcha_image_base64,
                "options": CaptchaOptionsSocketSer(**kwargs),
            }
        )

        return await self.send_request(normal_captcha_payload.dict())
'''
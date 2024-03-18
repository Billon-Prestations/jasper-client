import requests
import xmltodict
from urllib.parse import urlencode
from fastapi import HTTPException

AUTHORIZED_STATUS = 200
UNAUTHORIZED_STATUS = 401
HTTP_ERROR_401 = "Vous n'avez pas les autorisations pour accéder aux données."


class JasperClient:
    API_REST_PATH = "rest_v2/reports"
    API_REST_LISTING = "rest_v2/resources?resourceType=reportUnit"
    API_REST_LOGIN = "rest_v2/login"
    API_REST_EXPORT = "rest_v2/export"
    API_REST_IMPORT = "rest_v2/import"
    URL_INPUT_CONTROLS = "/inputControls/"
    URL_SUFFIXE = "/jasperserver/"

    TYPE_SINGLE_SELECT = "singleSelect"
    TYPE_SINGLE_VALUE_TEXT = "singleValueText"
    TYPE_SINGLE_VALUE_NUMBER = "singleValueNumber"

    def __init__(self, host: str, username: str, password: str):
        self.jasperUrl = host
        self.username = username
        self.password = password

    def getCookie(self):
        url = self.jasperUrl + JasperClient.API_REST_LOGIN
        postData = "?" + urlencode(
            {
                "j_username": self.username,
                "j_password": self.password,
            }
        )
        r = requests.post(url + postData)

        if r.status_code == AUTHORIZED_STATUS:
            self.cookie = r.cookies.get_dict()["JSESSIONID"]
            return "JSESSIONID=" + r.cookies.get_dict()["JSESSIONID"]

        if r.status_code == UNAUTHORIZED_STATUS:
            raise HTTPException(
                status_code=UNAUTHORIZED_STATUS,
                detail=HTTP_ERROR_401,
            )

    def get(self, url):
        return requests.get(url, headers={"Cookie": self.getCookie()})

    def _extract_report_units(self, xml_content):
        resources = xmltodict.parse(xml_content)["resources"]["resourceLookup"]
        return [res for res in resources if res["resourceType"] == "reportUnit"]

    def listReports(self):
        response = self.get(self.jasperUrl + JasperClient.API_REST_LISTING)
        return (
            self._extract_report_units(response.content)
            if response.status_code == AUTHORIZED_STATUS
            else []
        )

    def getReport(
        self, path: str, filename: str = "export", data: dict = {}, format: str = "pdf"
    ):
        response = self.get(
            self.jasperUrl
            + JasperClient.API_REST_PATH
            + path
            + "."
            + format
            + "?"
            + urlencode(data)
        )
        with open(f"{filename}.{format}", "wb") as output_file:
            output_file.write(response.content)
        return

    def getListParameters(
        self,
        path: str,
    ):
        r = self.get(
            self.jasperUrl
            + JasperClient.API_REST_PATH
            + path
            + JasperClient.URL_INPUT_CONTROLS
        )
        if r.status_code == AUTHORIZED_STATUS:
            return xmltodict.parse(r.content)
        return {
            "inputControls": {
                "inputControl": [],
            }
        }

    def _constructParamSubset(self, param: dict) -> dict:
        parameterSubset = {
            "id": param["id"],
            "label": param["label"],
            "type": param["type"],
            "mandatory": param["mandatory"],
        }

        if parameterSubset["type"] == JasperClient.TYPE_SINGLE_SELECT:
            parameterSubset["options"] = param["state"]["options"]["option"]

        return parameterSubset

    def getParameters(self, path: str):
        params = self.getListParameters(path)["inputControls"]["inputControl"]
        params = [params] if not isinstance(params, list) else params
        return [self._constructParamSubset(param) for param in params]

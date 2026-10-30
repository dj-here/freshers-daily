from typing import Dict, Type
from app.connectors.base import BaseConnector
from app.connectors.greenhouse import GreenhouseConnector
from app.connectors.lever import LeverConnector
from app.connectors.ashby import AshbyConnector
from app.connectors.smartrecruiters import SmartRecruitersConnector
from app.connectors.workable import WorkableConnector
from app.connectors.workday import WorkdayConnector
from app.connectors.official import OfficialCareerConnector
from app.connectors.manual import ManualSubmitConnector

CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {
    "greenhouse": GreenhouseConnector,
    "lever": LeverConnector,
    "ashby": AshbyConnector,
    "smartrecruiters": SmartRecruitersConnector,
    "workable": WorkableConnector,
    "workday": WorkdayConnector,
    "official": OfficialCareerConnector,
    "manual": ManualSubmitConnector,
}

def get_connector(source_type: str) -> BaseConnector:
    connector_cls = CONNECTOR_REGISTRY.get(source_type.lower())
    if not connector_cls:
        raise ValueError(f"Unsupported connector source type: {source_type}")
    return connector_cls()

from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class AssetRecord(Base):
    __tablename__ = "ai_assets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    asset_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    asset_type = Column(
        String(100),
        nullable=False,
    )

    model = Column(
        String(500),
        nullable=True,
    )

    provider = Column(
        String(500),
        nullable=True,
    )

    location = Column(
        String(255),
        nullable=True,
    )

    application = Column(
        String(255),
        nullable=True,
    )

    purpose = Column(
        Text,
        nullable=True,
    )

    tools = Column(
        Text,
        nullable=True,
    )

    discovery_source = Column(
        String(100),
        nullable=True,
    )

    status = Column(
        String(100),
        nullable=True,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    confidence = Column(
        String(50),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )
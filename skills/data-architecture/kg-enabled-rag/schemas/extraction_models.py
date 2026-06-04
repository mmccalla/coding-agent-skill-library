from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    aliases: list[str] = []
    evidence_child_chunk_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedRelationship(BaseModel):
    source_name: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    relationship_type: str = Field(min_length=1)
    target_name: str = Field(min_length=1)
    target_type: str = Field(min_length=1)
    evidence_child_chunk_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]

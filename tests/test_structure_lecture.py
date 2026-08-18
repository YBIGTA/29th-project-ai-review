from src.schemas import StructuredChunk
from src.config import LECTURES
from src.schemas import StructuredPageResponse
from src.structure_lecture import (
    _call_with_retries,
    _preserve_source_text,
    make_chunk_id,
)


def test_make_chunk_id():
    assert make_chunk_id("eda_fe", 15, 1) == "eda_fe_p15_01"


def test_raw_text_not_in_source_is_replaced():
    chunk = StructuredChunk(
        topic="평균",
        concepts=["평균"],
        raw_text="원문에 없는 문장",
        content="검색용 내용",
    )

    result = _preserve_source_text([chunk], "평균은 대표값이다.")

    assert result[0].raw_text == "평균은 대표값이다."


def test_exact_raw_text_is_preserved():
    chunk = StructuredChunk(
        topic="평균",
        concepts=["평균"],
        raw_text="평균은 대표값이다.",
        content="검색용 내용",
    )

    result = _preserve_source_text([chunk], "설명\n평균은 대표값이다.\n끝")

    assert result[0].raw_text == "평균은 대표값이다."


def test_page_request_contains_text_and_full_page_image():
    parsed = StructuredPageResponse(
        chunks=[
            StructuredChunk(
                topic="가설검정",
                concepts=["1종 오류", "2종 오류"],
                raw_text="",
                visual_description="두 분포와 오류 영역을 보여주는 그래프",
                content="귀무가설과 대립가설 분포의 오류 영역을 설명한다.",
            )
        ]
    )

    class FakeResponses:
        def __init__(self):
            self.kwargs = None

        def parse(self, **kwargs):
            self.kwargs = kwargs
            return type("Response", (), {"output_parsed": parsed})()

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    client = FakeClient()
    result = _call_with_retries(
        client=client,
        model="vision-model",
        lecture=LECTURES["basic_statistics"],
        page=13,
        segment="",
        segment_number=1,
        segment_count=1,
        image_data_url="data:image/png;base64,AAAA",
        vision_detail="original",
        previous_text="이전",
        next_text="다음",
        max_retries=1,
    )

    user_content = client.responses.kwargs["input"][1]["content"]
    assert result == parsed
    assert user_content[0]["type"] == "input_text"
    assert user_content[1] == {
        "type": "input_image",
        "image_url": "data:image/png;base64,AAAA",
        "detail": "original",
    }

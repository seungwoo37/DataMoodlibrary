datamood.text package
=====================

Datamood의 텍스트 처리 모듈로, 텍스트 기반 감정(무드) 분석을 위한 
전처리, 특징 추출, 감정 분류 기능을 제공합니다.  
텍스트 데이터로 감정 분석 모델을 구축하거나 문서 기반 무드 태깅을 수행할 때 활용됩니다.


Submodules
^^^^^^^^^^^

text_mood Module
-------------------------------

텍스트 데이터를 분석하여 감정 상태를 분류하는 핵심 모듈입니다.  
토큰화, 정규화, 임베딩 생성 및 감정 분류 모델과 연동하기 위한 기능을 포함합니다.

.. automodule:: datamood.text.text_mood
   :members:
   :show-inheritance:
   :undoc-members:

텍스트추출_저장 Module
-------------------------------------

문서, 파일, 문자열 등 다양한 소스에서 텍스트를 추출하고  
전처리된 결과를 저장하는 기능을 제공합니다.  
OCR 또는 자연어 처리 파이프라인의 입력 준비용 모듈로 활용할 수 있습니다.

.. automodule:: datamood.text.텍스트추출_저장
   :members:
   :show-inheritance:
   :undoc-members:


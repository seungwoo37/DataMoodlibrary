datamood package
================

Datamood는 오디오와 텍스트 데이터를 기반으로  
감정(무드) 분석을 수행하기 위한 기능들을 제공하는 통합 라이브러리입니다.  
데이터 전처리부터 특징 추출, 감정 분류 모델 실행까지  
AI 기반 무드 분석 워크플로우를 손쉽게 구축할 수 있도록 설계되었습니다.

Subpackages
-----------

아래는 Datamood의 주요 하위 패키지들입니다.

.. toctree::
   :maxdepth: 4

   datamood.audio
   datamood.text
   datamood.utils

Submodules
----------

CLI Module
^^^^^^^^^^^^^^^

명령줄 인터페이스(CLI)를 제공하여  
Datamood 기능을 터미널에서 직접 실행할 수 있게 해주는 모듈입니다.

.. automodule:: datamood.cli
   :members:
   :show-inheritance:
   :undoc-members:

mood_sorter Module
^^^^^^^^^^^^^^^^^^^^^^^^^

오디오·텍스트 데이터를 기반으로 감정(긍정/부정)을 분류하고  
결과를 일관된 형태로 제공하는 핵심 실행 모듈입니다.

.. automodule:: datamood.mood_sorter
   :members:
   :show-inheritance:
   :undoc-members:

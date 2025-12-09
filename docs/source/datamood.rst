datamood package
================

Datamood 패키지는 오디오와 텍스트 데이터를 기반으로 감정(무드)을 분석·정렬해주는
AI 기반 데이터 전처리 도구입니다.  
음성, 텍스트 처리 유틸리티는 물론, 간단한 CLI 환경까지 제공하여
데이터 감정 분석 워크플로우를 손쉽게 자동화할 수 있습니다.

Subpackages
-----------

아래는 datamood가 제공하는 주요 서브패키지입니다.

.. toctree::
   :maxdepth: 4

   datamood.audio
   datamood.text
   datamood.utils

Submodules
------------

CLI Module
^^^^^^^^^^^^^

명령줄 인터페이스(CLI)를 제공하는 모듈입니다.

.. automodule:: datamood.cli
   :members:
   :show-inheritance:
   :undoc-members:

mood_sorter Module
^^^^^^^^^^^^^^^^^^^^

텍스트와 오디오 데이터를 기반으로 감정을 분류·정렬하는 핵심 모듈입니다.

.. automodule:: datamood.mood_sorter
   :members:
   :show-inheritance:
   :undoc-members:

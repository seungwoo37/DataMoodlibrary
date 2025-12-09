Usage
=====

Installation
------------

To use datamood, first install it using pip:

..code-block:: console
    (.venv) $ pip install SpeechRecognition
    (.venv) $ pip install konlpy
    (.venv) $ pip install yt-dlp
    (.venv) $ pip install pydub
    (.venv) $ pip install beautifulsoup4
    (.venv) $ pip install requests
    (.venv) $ pip install jpypel
    
    **Additional System Dependency: FFmpeg**

The 'pydub' library requires **FFmpeg** to process audio files. FFmpeg must be installed separately based on your operating system.

**1. Windows**

1.  Download the latest FFmpeg build from the official FFmpeg site or a reliable mirror (e.g., gyan.dev).
2.  Extract the downloaded zip file to a convenient location (e.g., C:\FFmpeg).
3.  Add the **\bin** directory (e.g., C:\FFmpeg\bin) to your system's **PATH** environment variable.

**2. macOS**

You can install FFmpeg easily using **Homebrew**:

.. code-block:: console

    $ brew install ffmpeg

**3. Linux (Debian/Ubuntu)**

Use the system package manager **apt**:

.. code-block:: console

    $ sudo apt update
    $ sudo apt install ffmpeg
    
# For other Linux distributions, please use the appropriate package manager (e.g., 'yum install ffmpeg' for CentOS/RHEL).


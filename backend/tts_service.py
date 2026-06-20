"""
TTS-palvelu: generoi .wav-äänitiedoston suomenkielisestä tekstistä
käyttäen F5-TTS -mallia HuggingFacesta.
"""

import io
import tempfile
from pathlib import Path

import numpy as np
import requests
import soundfile as sf
import torch
from cached_path import cached_path
from huggingface_hub import hf_hub_download
from hydra.utils import get_class
from omegaconf import OmegaConf

from f5_tts.infer.utils_infer import (
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
)

class TTSService:
    """Suomenkielinen TTS-palvelu F5-TTS -mallilla."""

    def __init__(self, model_name: str, cache_dir: Path | None = None, ref_audio_path: str | None = None, ref_text: str | None = None):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.ema_model = None
        self.vocoder = None
        self.vocab_file = None
        self.ref_audio_path = ref_audio_path
        self.ref_text = ref_text
        self.sample_rate = 24000
        self._loaded = False

    @property
    def device(self) -> str:
        """Palauta käytettävä laite: 'cuda' jos saatavilla, muuten 'cpu'."""
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self):
        """Lataa F5-TTS -malli HuggingFacesta."""
        if self._loaded:
            return

        print(f"Ladataan TTS-malli: {self.model_name}")

        # Lataa malli ja sanakirja HuggingFacesta
        # F5-TTS Finnish Model: uusin versio (v1, 20250323)
        model_path = hf_hub_download(
            repo_id=self.model_name,
            filename="model_commonvoice_fi_librivox_fi_vox_populi_fi_20250323/model_last_20250323.safetensors",
            cache_dir=self.cache_dir,
        )
        vocab_path = hf_hub_download(
            repo_id=self.model_name,
            filename="vocab.txt",
            cache_dir=self.cache_dir,
        )

        self.vocab_file = vocab_path

        # Lataa reference-ääni (prompt) — tarvitaan F5-TTS:n toimintaan
        # Jos ei ole reference-ääntä, käytetään mallin oletusarvoa
        # F5-TTS vaatii reference-äänen (prompt) ja sen transkription
        # Ladataan reference-ääni HuggingFacesta
        if self.ref_audio_path is None:
            try:
                # V1-mallin (20250323) reference-ääni ja -teksti
                ref_audio_path = hf_hub_download(
                    repo_id=self.model_name,
                    filename="model_commonvoice_fi_librivox_fi_vox_populi_fi_20250323/AsmoKoskinenRef_v1.wav",
                    cache_dir=self.cache_dir,
                )
                # Varmista että tiedosto on ladattu (ei 0-bytinen)
                if Path(ref_audio_path).stat().st_size > 0:
                    self.ref_audio_path = ref_audio_path
                    # Lataa myös reference-teksti
                    try:
                        ref_text_path = hf_hub_download(
                            repo_id=self.model_name,
                            filename="model_commonvoice_fi_librivox_fi_vox_populi_fi_20250323/AsmoKoskinenRef_v1.txt",
                            cache_dir=self.cache_dir,
                        )
                        if Path(ref_text_path).stat().st_size > 0:
                            with open(ref_text_path, "r", encoding="utf-8") as f:
                                self.ref_text = f.read().strip()
                    except Exception:
                        print("VAROITUS: Ei reference-tekstiä löydy!")
                else:
                    raise Exception("Tiedosto on tyhjä")
            except Exception:
                # Jos ei ole reference-ääntä, käytetään mallin oletusarvoa
                # Tämä ei todennäköisesti toimi, koska F5-TTS vaatii reference-äänen
                print("VAROITUS: Ei reference-ääntä löydy!")
                return

        # Lataa vocoder (Vocos)
        self.vocoder = load_vocoder(
            vocoder_name="vocos",
            is_local=False,
            local_path=None,
            device=self.device,
        )

        # Lataa malli
        # Config-tiedosto ei ole HuggingFace-repositoriossa, vaan GitHubissa
        # Ladataan se suoraan GitHubista
        config_url = "https://raw.githubusercontent.com/SWivid/F5-TTS/main/src/f5_tts/configs/F5TTS_v1_Base.yaml"
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8") as tmp:
            response = requests.get(config_url, timeout=60)
            response.raise_for_status()
            tmp.write(response.text)
            tmp.flush()
            config_path = tmp.name

        model_cfg = OmegaConf.load(config_path)
        model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")

        self.ema_model = load_model(
            model_cls,
            model_cfg.model.arch,
            model_path,
            mel_spec_type="vocos",
            vocab_file=self.vocab_file,
            device=self.device,
        )

        self._loaded = True
        print("TTS-malli ladattu onnistuneesti!")

    def generate(self, text: str) -> bytes:
        """
        Generoi .wav-äänitiedoston suomenkielisestä tekstistä.

        Args:
            text: Suomenkielinen teksti, josta generoidaan ääni.

        Returns:
            .wav-tiedoston sisältö bytes-muodossa.
        """
        if not self._loaded:
            self._load_model()

        if self.ref_audio_path is None:
            raise RuntimeError(
                "Ei reference-ääntä löydy! TTS generointi vaatii reference-äänen. "
                "Varmista että HuggingFace-repositoriossa on reference-ääni "
                "tai aseta ref_audio_path TTSService:n alustuksessa."
            )

        # F5-TTS vaatii reference-äänen (prompt) ja sen transkription
        # Käytetään mallin mukana tulevaa reference-ääntä
        ref_audio, ref_text = preprocess_ref_audio_text(
            self.ref_audio_path,
            self.ref_text or "",
        )

        # Generoi ääni
        audio_segment, final_sample_rate, spectrogram = infer_process(
            ref_audio,
            ref_text,
            text,
            self.ema_model,
            self.vocoder,
            mel_spec_type="vocos",
            target_rms=0.1,
            cross_fade_duration=0.15,
            nfe_step=32,
            cfg_strength=4.0,
            sway_sampling_coef=None,
            speed=0.9,
            fix_duration=None,
            device=self.device,
        )

        # Tallenna .wav-tiedosto
        buf = io.BytesIO()
        sf.write(buf, audio_segment, final_sample_rate, format="WAV")
        buf.seek(0)
        return buf.read()

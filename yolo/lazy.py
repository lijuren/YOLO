import sys
from pathlib import Path

import hydra
from lightning import Trainer

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from yolo.config.config import Config
from yolo.tools.solver import InferenceModel, TrainModel, ValidateModel
from yolo.utils.logging_utils import setup


@hydra.main(config_path="config", config_name="config", version_base=None)
def main(cfg: Config):
    callbacks, loggers, save_path = setup(cfg)

    trainer = Trainer(
        accelerator="cuda",
        max_epochs=getattr(cfg.task, "epoch", None),
        precision="16-mixed",
        callbacks=callbacks,
        logger=loggers,
        log_every_n_steps=1,
        gradient_clip_val=10,
        deterministic=True,
        enable_progress_bar=not getattr(cfg, "quite", False),
        default_root_dir=save_path,
    )

    match cfg.task.task:
        case "train":
            model = TrainModel(cfg)
            trainer.fit(model)
        case "validation":
            model = ValidateModel(cfg)
            trainer.validate(model)
        case "inference":
            model = InferenceModel(cfg)
            trainer.predict(model)


if __name__ == "__main__":
    main()

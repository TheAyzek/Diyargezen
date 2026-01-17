from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import checkbox
from ..utils.feats import calculate_available_feat_count, check_feat_prerequisites
from .base import Step, StepResult


@dataclass
class FeatsStep(Step):
    name: str = "feats"
    description: str = "Feat seçimi"
    feats_data: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.feats_data:
            return StepResult(True, "Feat verisi bulunamadı, adım atlandı.")

        # Level-up sırasında kullanıcı ASI seçtiyse feat adımını atla
        asi_mode = ctx.metadata.get("asi_mode")
        if asi_mode == "ASI":
            return StepResult(True, "ASI seçildiği için feat adımı atlandı.")

        feat_count = calculate_available_feat_count(ctx.level, ctx.race or "")
        if feat_count <= 0:
            return StepResult(True, "Bu seviyede feat alınamaz.")

        available_items = []
        for feat_name, feat_data in sorted(self.feats_data.items()):
            prereq = feat_data.get("prerequisites", {})
            meets = check_feat_prerequisites(ctx, prereq)
            label = feat_name
            if prereq:
                label += " (gereksinimler var"
                if not meets:
                    label += " - KARŞILANMIYOR"
                label += ")"
            if meets:
                available_items.append(label)

        if not available_items:
            return StepResult(True, "Gereksinimleri karşılayan feat yok.")

        picked_labels = checkbox(
            f"Feat seçimi (en fazla {feat_count} adet):",
            available_items,
            min_selected=0,
            max_selected=feat_count,
        )

        picked_names = [label.split(" (")[0] for label in picked_labels]
        ctx.features.extend(picked_names)
        ctx.metadata["selected_feats"] = picked_names
        return StepResult(True, "Feat seçimi tamamlandı.")



from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import checkbox
from ..utils.feats import calculate_available_feat_count, check_feat_prerequisites
from .base import Step, StepResult


@dataclass
class FeatsStep(Step):
    name: str = "feats"
    description: str = "Feat seçimi"
    feats_data: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.feats_data:
            return StepResult(True, "Feat verisi bulunamadı, adım atlandı.")

        # Level-up sırasında kullanıcı ASI seçtiyse feat adımını atla
        asi_mode = ctx.metadata.get("asi_mode")
        if asi_mode == "ASI":
            return StepResult(True, "ASI seçildiği için feat adımı atlandı.")

        feat_count = calculate_available_feat_count(ctx.level, ctx.race or "")
        if feat_count <= 0:
            return StepResult(True, "Bu seviyede feat alınamaz.")

        available_items = []
        for feat_name, feat_data in sorted(self.feats_data.items()):
            prereq = feat_data.get("prerequisites", {})
            meets = check_feat_prerequisites(ctx, prereq)
            label = feat_name
            if prereq:
                label += " (gereksinimler var"
                if not meets:
                    label += " - KARŞILANMIYOR"
                label += ")"
            if meets:
                available_items.append(label)

        if not available_items:
            return StepResult(True, "Gereksinimleri karşılayan feat yok.")

        picked_labels = checkbox(
            f"Feat seçimi (en fazla {feat_count} adet):",
            available_items,
            min_selected=0,
            max_selected=feat_count,
        )

        picked_names = [label.split(" (")[0] for label in picked_labels]
        ctx.features.extend(picked_names)
        ctx.metadata["selected_feats"] = picked_names
        return StepResult(True, "Feat seçimi tamamlandı.")



from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import checkbox
from ..utils.feats import calculate_available_feat_count, check_feat_prerequisites
from .base import Step, StepResult


@dataclass
class FeatsStep(Step):
    name: str = "feats"
    description: str = "Feat seçimi"
    feats_data: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.feats_data:
            return StepResult(True, "Feat verisi bulunamadı, adım atlandı.")

        # Level-up sırasında kullanıcı ASI seçtiyse feat adımını atla
        asi_mode = ctx.metadata.get("asi_mode")
        if asi_mode == "ASI":
            return StepResult(True, "ASI seçildiği için feat adımı atlandı.")

        feat_count = calculate_available_feat_count(ctx.level, ctx.race or "")
        if feat_count <= 0:
            return StepResult(True, "Bu seviyede feat alınamaz.")

        available_items = []
        for feat_name, feat_data in sorted(self.feats_data.items()):
            prereq = feat_data.get("prerequisites", {})
            meets = check_feat_prerequisites(ctx, prereq)
            label = feat_name
            if prereq:
                label += " (gereksinimler var"
                if not meets:
                    label += " - KARŞILANMIYOR"
                label += ")"
            if meets:
                available_items.append(label)

        if not available_items:
            return StepResult(True, "Gereksinimleri karşılayan feat yok.")

        picked_labels = checkbox(
            f"Feat seçimi (en fazla {feat_count} adet):",
            available_items,
            min_selected=0,
            max_selected=feat_count,
        )

        picked_names = [label.split(" (")[0] for label in picked_labels]
        ctx.features.extend(picked_names)
        ctx.metadata["selected_feats"] = picked_names
        return StepResult(True, "Feat seçimi tamamlandı.")



from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import checkbox
from ..utils.feats import calculate_available_feat_count, check_feat_prerequisites
from .base import Step, StepResult


@dataclass
class FeatsStep(Step):
    name: str = "feats"
    description: str = "Feat seçimi"
    feats_data: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.feats_data:
            return StepResult(True, "Feat verisi bulunamadı, adım atlandı.")

        # Level-up sırasında kullanıcı ASI seçtiyse feat adımını atla
        asi_mode = ctx.metadata.get("asi_mode")
        if asi_mode == "ASI":
            return StepResult(True, "ASI seçildiği için feat adımı atlandı.")

        feat_count = calculate_available_feat_count(ctx.level, ctx.race or "")
        if feat_count <= 0:
            return StepResult(True, "Bu seviyede feat alınamaz.")

        available_items = []
        for feat_name, feat_data in sorted(self.feats_data.items()):
            prereq = feat_data.get("prerequisites", {})
            meets = check_feat_prerequisites(ctx, prereq)
            label = feat_name
            if prereq:
                label += " (gereksinimler var"
                if not meets:
                    label += " - KARŞILANMIYOR"
                label += ")"
            if meets:
                available_items.append(label)

        if not available_items:
            return StepResult(True, "Gereksinimleri karşılayan feat yok.")

        picked_labels = checkbox(
            f"Feat seçimi (en fazla {feat_count} adet):",
            available_items,
            min_selected=0,
            max_selected=feat_count,
        )

        picked_names = [label.split(" (")[0] for label in picked_labels]
        ctx.features.extend(picked_names)
        ctx.metadata["selected_feats"] = picked_names
        return StepResult(True, "Feat seçimi tamamlandı.")



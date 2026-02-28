<template>
  <v-dialog
    :model-value="modelValue"
    max-width="560"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="d-flex align-center gap-2">
        <v-icon color="primary">
          {{ $globals.icons.pantry }}
        </v-icon>
        Check Your Pantry
      </v-card-title>
      <v-card-subtitle class="pb-2">
        Update remaining quantities for ingredients you used.
      </v-card-subtitle>

      <v-card-text>
        <div
          v-if="ingredients.length === 0"
          class="text-medium-emphasis py-4 text-center"
        >
          No food ingredients found for this recipe.
        </div>
        <v-list
          v-else
          density="compact"
        >
          <v-list-item
            v-for="ingredient in ingredients"
            :key="ingredient.referenceId || ingredient.foodName"
            class="px-0"
          >
            <template #default>
              <div class="py-2">
                <!-- Food name + recipe quantity -->
                <div class="d-flex align-center mb-1">
                  <span class="text-body-2 font-weight-medium">{{ ingredient.foodName }}</span>
                  <span
                    v-if="ingredient.quantity || ingredient.unit"
                    class="text-caption text-medium-emphasis ml-2"
                  >
                    (recipe: {{ ingredient.quantity ?? "" }} {{ ingredient.unit ?? "" }})
                  </span>
                </div>

                <!-- Remaining quantity row -->
                <div class="d-flex align-center gap-2">
                  <v-text-field
                    v-model.number="depletions[ingredient.foodId || ingredient.referenceId].quantity"
                    type="number"
                    min="0"
                    density="compact"
                    variant="outlined"
                    hide-details
                    label="Remaining"
                    style="max-width: 120px;"
                  />
                  <span
                    v-if="ingredient.unit"
                    class="text-body-2 text-medium-emphasis"
                    style="min-width: 48px;"
                  >{{ ingredient.unit }}</span>

                  <v-btn-toggle
                    v-model="depletions[ingredient.foodId || ingredient.referenceId].status"
                    density="compact"
                    variant="outlined"
                    color="primary"
                    mandatory
                    class="ml-auto"
                  >
                    <v-btn value="ok" size="small">
                      OK
                    </v-btn>
                    <v-btn value="low" size="small" color="warning">
                      Low
                    </v-btn>
                    <v-btn value="out" size="small" color="error">
                      Out
                    </v-btn>
                  </v-btn-toggle>
                </div>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions>
        <v-btn
          variant="text"
          @click="cancel"
        >
          Skip
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          :loading="saving"
          @click="confirm"
        >
          Update Pantry
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { usePantryApi } from "~/composables/api/use-pantry-api";
import { alert } from "~/composables/use-toast";

interface RecipeIngredientRef {
  referenceId: string;
  foodId?: string | null;
  foodName: string;
  quantity?: number | null;
  unit?: string | null;
}

interface DepletionEntry {
  status: "ok" | "low" | "out";
  quantity: number | null;
}

const props = defineProps<{
  modelValue: boolean;
  recipeSlug: string;
  ingredients: RecipeIngredientRef[];
}>();

const emit = defineEmits<{
  "update:modelValue": [val: boolean];
  done: [];
}>();

const pantryApi = usePantryApi();
const saving = ref(false);

// depletions: key → { status, quantity }
const depletions = ref<Record<string, DepletionEntry>>({});

// On mount or when ingredients change, fetch pantry cross-ref to pre-fill quantities
async function initDepletions() {
  const map: Record<string, DepletionEntry> = {};
  for (const ing of props.ingredients) {
    const key = ing.foodId || ing.referenceId;
    map[key] = { status: "ok", quantity: null };
  }

  // Pre-fill from pantry
  if (props.recipeSlug) {
    const { data } = await pantryApi.getRecipePantryIngredients(props.recipeSlug);
    if (data) {
      for (const row of data) {
        const key = row.food_id || row.reference_id;
        if (key && map[key] !== undefined) {
          const pantryQty = row.pantry_items?.[0]?.quantity ?? null;
          map[key].quantity = pantryQty;
        }
      }
    }
  }

  depletions.value = map;
}

watchEffect(() => {
  if (props.modelValue) {
    initDepletions();
  }
});

async function confirm() {
  saving.value = true;
  const deplList = props.ingredients
    .filter(ing => ing.foodId)
    .map(ing => ({
      foodId: ing.foodId!,
      status: depletions.value[ing.foodId!]?.status || "ok",
      quantity: depletions.value[ing.foodId!]?.quantity ?? null,
    }));

  if (deplList.length > 0) {
    const { error } = await pantryApi.cookingCheck({
      recipeSlug: props.recipeSlug,
      depletions: deplList,
    });

    if (!error) {
      alert.success("Pantry updated!");
    }
    else {
      alert.error("Failed to update pantry");
    }
  }

  saving.value = false;
  emit("update:modelValue", false);
  emit("done");
}

function cancel() {
  emit("update:modelValue", false);
}
</script>

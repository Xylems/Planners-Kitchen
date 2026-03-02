<template>
  <v-dialog
    :model-value="modelValue"
    max-width="580"
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

        <template v-else>
          <!-- ── Existing pantry items (qty+unit from pantry; recipe qty shown as context) ── -->
          <template v-if="existingIngredients.length > 0">
            <div class="text-overline text-medium-emphasis mb-1">
              In Your Pantry
            </div>
            <v-list density="compact">
              <v-list-item
                v-for="ingredient in existingIngredients"
                :key="ingredient.referenceId || ingredient.foodId"
                class="px-0"
              >
                <template #default>
                  <div class="py-2">
                    <div class="d-flex align-center mb-1">
                      <span class="text-body-2 font-weight-medium">{{ ingredient.foodName }}</span>
                      <span
                        v-if="ingredient.quantity || ingredient.unit"
                        class="text-caption text-medium-emphasis ml-2"
                      >
                        (recipe: {{ ingredient.quantity ?? "" }} {{ ingredient.unit ?? "" }})
                      </span>
                    </div>
                    <div class="d-flex align-center gap-2 flex-wrap">
                      <v-text-field
                        v-model.number="depletions[ingredient.foodId!].quantity"
                        type="number"
                        min="0"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Remaining"
                        style="max-width: 110px;"
                      />
                      <!-- Show pantry unit (e.g. gallons) if available; fall back to recipe unit -->
                      <span
                        v-if="depletions[ingredient.foodId!].pantryUnit || ingredient.unit"
                        class="text-body-2 text-medium-emphasis"
                        style="min-width: 40px;"
                      >{{ depletions[ingredient.foodId!].pantryUnit || ingredient.unit }}</span>
                      <v-text-field
                        v-model="depletions[ingredient.foodId!].expirationDate"
                        type="date"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Expiry date"
                        style="max-width: 160px;"
                      />
                      <v-btn-toggle
                        v-model="depletions[ingredient.foodId!].status"
                        density="compact"
                        variant="outlined"
                        color="primary"
                        mandatory
                        class="ml-auto"
                      >
                        <v-btn value="ok" size="small">OK</v-btn>
                        <v-btn value="low" size="small" color="warning">Low</v-btn>
                        <v-btn value="out" size="small" color="error">Out</v-btn>
                      </v-btn-toggle>
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </template>

          <!-- ── New items (not yet in pantry) ── -->
          <template v-if="newIngredients.length > 0">
            <v-divider v-if="existingIngredients.length > 0" class="my-3" />
            <div class="d-flex align-center gap-1 text-overline text-medium-emphasis mb-1">
              <v-icon size="small" color="primary">{{ $globals.icons.plus }}</v-icon>
              New to Pantry
            </div>
            <v-list density="compact">
              <v-list-item
                v-for="ingredient in newIngredients"
                :key="ingredient.referenceId || ingredient.foodId"
                class="px-0"
              >
                <template #default>
                  <div class="py-2">
                    <div class="d-flex align-center mb-2">
                      <span class="text-body-2 font-weight-medium">{{ ingredient.foodName }}</span>
                      <span
                        v-if="ingredient.quantity || ingredient.unit"
                        class="text-caption text-medium-emphasis ml-2"
                      >
                        (recipe: {{ ingredient.quantity ?? "" }} {{ ingredient.unit ?? "" }})
                      </span>
                    </div>
                    <!-- Row 1: qty + unit + expiry + status -->
                    <div class="d-flex align-center gap-2 flex-wrap mb-2">
                      <v-text-field
                        v-model.number="depletions[ingredient.foodId!].quantity"
                        type="number"
                        min="0"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Remaining"
                        style="max-width: 110px;"
                      />
                      <span
                        v-if="ingredient.unit"
                        class="text-body-2 text-medium-emphasis"
                        style="min-width: 40px;"
                      >{{ ingredient.unit }}</span>
                      <v-text-field
                        v-model="depletions[ingredient.foodId!].expirationDate"
                        type="date"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Expiry date"
                        style="max-width: 160px;"
                      />
                      <v-btn-toggle
                        v-model="depletions[ingredient.foodId!].status"
                        density="compact"
                        variant="outlined"
                        color="primary"
                        mandatory
                        class="ml-auto"
                      >
                        <v-btn value="ok" size="small">OK</v-btn>
                        <v-btn value="low" size="small" color="warning">Low</v-btn>
                        <v-btn value="out" size="small" color="error">Out</v-btn>
                      </v-btn-toggle>
                    </div>
                    <!-- Row 2: location + category -->
                    <div class="d-flex gap-2">
                      <v-text-field
                        v-model="depletions[ingredient.foodId!].location"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Location (e.g. Fridge, Pantry shelf)"
                        class="flex-grow-1"
                      />
                      <v-text-field
                        v-model="depletions[ingredient.foodId!].category"
                        density="compact"
                        variant="outlined"
                        hide-details
                        label="Category (e.g. Dairy, Spices)"
                        class="flex-grow-1"
                      />
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </template>
        </template>
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
  expirationDate: string | null;
  location: string | null;
  category: string | null;
  pantryUnit: string | null;
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

const depletions = ref<Record<string, DepletionEntry>>({});
const newItemFoodIds = ref<Set<string>>(new Set());

const existingIngredients = computed(() =>
  props.ingredients.filter(ing => {
    const key = ing.foodId || ing.referenceId;
    return key && !newItemFoodIds.value.has(key);
  }),
);

const newIngredients = computed(() =>
  props.ingredients.filter(ing => {
    const key = ing.foodId || ing.referenceId;
    return key && newItemFoodIds.value.has(key);
  }),
);

async function initDepletions() {
  // Set depletions immediately (before await) so the template has valid entries on first render
  const map: Record<string, DepletionEntry> = {};
  for (const ing of props.ingredients) {
    const key = ing.foodId || ing.referenceId;
    if (key) {
      map[key] = { status: "ok", quantity: null, expirationDate: null, location: null, category: null, pantryUnit: null };
    }
  }
  depletions.value = map;
  newItemFoodIds.value = new Set();

  if (!props.recipeSlug) return;

  const newIds = new Set<string>();
  const { data } = await pantryApi.getRecipePantryIngredients(props.recipeSlug);
  if (data) {
    for (const row of data) {
      const key = row.food_id || row.reference_id;
      if (key && depletions.value[key] !== undefined) {
        if (row.pantry_items?.length > 0) {
          // Pre-fill from existing pantry item — use reactive ref so Vue picks up changes
          depletions.value[key].quantity = row.pantry_items[0].quantity ?? null;
          depletions.value[key].expirationDate = row.pantry_items[0].expiration_date ?? null;
          depletions.value[key].pantryUnit = row.pantry_items[0].unit ?? null;
        }
        else {
          // No existing pantry item — mark as new
          newIds.add(key);
        }
      }
    }
  }

  newItemFoodIds.value = newIds;
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
      status: depletions.value[ing.foodId!]?.status ?? "ok",
      quantity: depletions.value[ing.foodId!]?.quantity ?? null,
      unit: ing.unit ?? null,
      expirationDate: depletions.value[ing.foodId!]?.expirationDate ?? null,
      location: depletions.value[ing.foodId!]?.location ?? null,
      category: depletions.value[ing.foodId!]?.category ?? null,
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

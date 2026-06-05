<template>
  <v-card class="mx-auto my-5" max-width="500" elevation="2">
    <v-card-text>
      <v-row>
        <v-col v-if="title" cols="4" class="d-flex justify-center align-center">
          <h3>{{ title }}</h3>
        </v-col>
        <v-col>
          <audio controls>
            <source :src="audioURL" type="audio/wav" />
          </audio>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  audioURL: { type: String, required: true },
})
</script>

<style>
.text-center {
  text-align: center;
}
</style>

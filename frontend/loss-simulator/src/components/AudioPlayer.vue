<template>
    <v-card class="mx-auto my-5" max-width="500" elevation="2">
      <v-card-text>
        <v-row>
          <v-col v-if="title && title.length > 0" cols="4" class="d-flex justify-center align-center">
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

<script>
export default {
  name: 'AudioPlayer',
  props: {
    title: {
      type: String,
      default: ""
    },
    audioURL: {
      type: String
    }
  },
}
</script>

<style>
.text-center {
  text-align: center;
}
</style>
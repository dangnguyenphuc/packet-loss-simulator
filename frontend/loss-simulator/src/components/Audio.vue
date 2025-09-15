<template>
  <v-app>
    <v-main>
      <v-container class="text-center">
        <h1>Play Local WAV Audio</h1>
        <v-card class="mx-auto my-5" max-width="500" elevation="2">
          <v-card-text>
            <audio controls>
              <source src="/home/dangnp/workspace/loss-simulator/lossSimulator/static/audio.wav" type="audio/wav">
              Your browser does not support the audio element.
            </audio>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="playAudio">Play</v-btn>
            <v-btn color="error" @click="pauseAudio">Pause</v-btn>
          </v-card-actions>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'Audio',
  methods: {
    playAudio() {
      const audio = document.querySelector('audio');
      audio.play();
    },
    pauseAudio() {
      const audio = document.querySelector('audio');
      audio.pause();
    }
  }
}
</script>

<style>
.text-center {
  text-align: center;
}
</style>
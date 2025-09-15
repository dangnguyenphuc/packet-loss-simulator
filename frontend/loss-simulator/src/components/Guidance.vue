<template>
    <div>
        <pre>{{content}}</pre>
    </div>
</template>

<script>
export default {
    name: "Guidance",
    props: {
        content: String,
    }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap; 
  text-align: left;
}
</style>
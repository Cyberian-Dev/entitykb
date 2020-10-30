<script>
    export let choice = "admin";

    function setChoice(e) {
        window.$(".menu .active").removeClass("active");
        choice = e.target.id;
    }

    $: window.$("#" + choice).addClass("active");

</script>

<div class="ui top menu">
  <div class="item">
      <i class="large lightbulb outline icon"></i>
  </div>
  <a id="admin" class="active item" on:click={setChoice}>Admin</a>
  <a id="api" class="item" on:click={setChoice}>API</a>
  <a id="docs" class="item" on:click={setChoice}>Docs</a>
</div>

<style>
div.top.menu {
    border: 0;
    font-size: 1.4em;
}
</style>
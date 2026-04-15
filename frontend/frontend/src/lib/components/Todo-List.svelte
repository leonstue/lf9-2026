<script>
    let { name, id, ondelete } = $props();
</script>

<div class="list-item">
    <a href="/list/{id}">{name}</a>
    <button onclick={() => ondelete(id)}>Delete</button>
</div>

<style>
    .list-item {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 4px 0;
    }
</style>

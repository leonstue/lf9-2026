<script>
    import TodoList from "$lib/components/Todo-List.svelte";
    import { onMount } from "svelte";

    const API = "http://127.0.0.1:5000";
    let lists = $state([]);
    let newName = $state("");

    onMount(() => {
        loadLists();
    });

    async function loadLists() {
        const res = await fetch(`${API}/todo-list`);
        if (res.ok) lists = await res.json();
    }

    async function addList() {
        if (!newName.trim()) return;
        await fetch(`${API}/todo-list`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newName })
        });
        newName = "";
        await loadLists();
    }

    async function deleteList(id) {
        await fetch(`${API}/todo-list/${id}`, { method: "DELETE" });
        await loadLists();
    }
</script>

<h1>Todo Lists</h1>

<div class="lists">
    <input bind:value={newName} placeholder="New list name" />
    <button onclick={addList}>Add</button>
</div>

{#each lists as list}
    <TodoList name={list.name} id={list.id} ondelete={deleteList} />
{/each}

<style>
    .lists {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }
</style>

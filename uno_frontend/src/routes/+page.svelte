<script>

    import { goto } from "$app/navigation";
    import { gsap } from "gsap";
    import { onMount } from 'svelte';

    const api = import.meta.env.VITE_BACKEND_API
    const protocol = import.meta.env.VITE_SSL_BOOL == 'TRUE' ? 'https' : 'http';
    let scriptLoaded = false
    const pfp_list = Array.from({length: 5 + 1}, (_, i) => `pfp/${i}.jpg`);
    let current_pfp = pfp_list[Math.floor(Math.random()*pfp_list.length)];

    function loadTurnstileScript() {
        if (scriptLoaded) return;
        
        const script = document.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
        script.async = true;
        script.defer = true;
        document.body.appendChild(script);
        scriptLoaded = true;
    }


    function initialize(){
        loadTurnstileScript()
        let main_container = document.getElementById('main')

        gsap.to(
            main_container,
            {
                opacity:1,        
            onComplete: (()=>{
            let my_elem = document.getElementById('main_elements')
            gsap.to(my_elem,{opacity:1,duration:2})
        })})
    }


   
    
    function private_main(){
        let room_selector = document.getElementById('room_selector')
        let private_selector = document.getElementById('private_selector')
        gsap.to(room_selector,{opacity:0, rotateX:90, onComplete: (()=>{
            private_selector.classList.remove('hidden')
            gsap.from(
                private_selector,{rotateX:-90,opacity:0}
            )
            
        })})
    }

    async function public_main(){
        try {
                let session_id = sessionStorage.getItem('sessionid')
                const apiUrl = `${protocol}://${api}/public_join?session_id=${session_id}`;
                
                const response = await fetch(apiUrl,
                    {
                        method:'POST',
                    }
                );
                if(response.status == 200){
                    goto('/game')
                }
                else if (response.status == 204){
                    alert('No Public Games Available')
                }
                else{
                    goto('/')
                }

            } catch (error) {
                console.error('Error during fetch:', error);
                goto('/')
            }
    }

    async function private_join(){
        let game_id = window.prompt('CODE','')
        try {
                let session_id = sessionStorage.getItem('sessionid')
                const apiUrl = `${protocol}://${api}/join?session_id=${session_id}&game_id=${game_id}`;
                
                const response = await fetch(apiUrl,
                    {
                        method:'POST',
                    }
                );
                if(response.status == 200){
                    goto('/game')
                }
                else{
                    goto('/')
                }

            } catch (error) {
                console.error('Error during fetch:', error);
                goto('/')
            }
    }   
    
    async function private_create(){
            try {
                let session_id = sessionStorage.getItem('sessionid')
                const apiUrl = `${protocol}://${api}/create_game?session_id=${session_id}`;
                
                const response = await fetch(apiUrl,
                    {
                        method:'POST',
                    }
                );
                if(response.status == 200){
                    goto('/game')
                }
                else{
                    goto('/')
                }

            } catch (error) {
                console.error('Error during fetch:', error);
                goto('/')
            }
        }
  
    function pfp_change(direction){
        let current_index = pfp_list.indexOf(current_pfp)
    
        if (direction == 'left'){
            if (current_index == 0){
                current_pfp = pfp_list[pfp_list.length-1]
            }
            else{
                current_pfp = pfp_list[current_index-1]
            }
        }
        else if (direction == 'right'){
            if (current_index == pfp_list.length-1){
                current_pfp = pfp_list[0]
            }
            else{
                current_pfp = pfp_list[current_index+1]
            }
        }
    }

    async function form_submit(event){
            document.getElementById('button').disabled = true
            let formData = {}
            event.preventDefault();
            const form = event.target;
            const turnstileInput = form.querySelector('.cf-turnstile input[name="cf-turnstile-response"]');
            const turnstileResponse = turnstileInput ? turnstileInput.value : '';

            if (!turnstileResponse) {
                alert('Please wait until we verify your request')
                window.location.reload();
                return;
            }

            formData.turnstile_response = turnstileResponse;
            formData.name = form.querySelector('#name').value;
            formData.pfp = current_pfp

            const response = await fetch(`${protocol}://${api}/get_session`, {
                method: 'POST',
                body: JSON.stringify(formData),
            });

            const data = await response.json();
            const response_code = response.status
            if (response_code == 200){
                let session = data.sessionid
                sessionStorage.setItem('sessionid',session);
            }
            else
            {
                alert('Login Failed')
                window.location.reload();
                return
            }
            let main_container = document.getElementById('main')
            let main_container_class = main_container?.classList
            let room_selector = document.getElementById('room_selector')
            let room_selector_class = room_selector?.classList
           
            main_container_class?.add('blur-lg')
            room_selector_class?.remove('hidden')
            gsap.from(
                room_selector,{opacity:0,height:0}
            )
    }

    onMount(() => {
        initialize()
        })

</script>

<div class="app-width:hidden h-screen w-full bg-gray-950 flex justify-center items-center text-6xl text-white text-center">
    Only for Big Screens
</div>


<div class="flex-col justify-center bg-[#5472E4] h-screen w-full overflow-hidden hidden app-width:flex">
    <div id="room_selector" class="absolute z-40 h-1/3 w-full hidden">
            <div class="flex rounded-2xl shadow-lg w-1/2 h-full bg-blue-600 mx-auto items-center">
                <button on:click={public_main} class="border-4 border-green-400 mx-auto h-1/3 w-1/3 rounded-2xl text-4xl bg-green-400 text-black font-bold hover:border-green-600 shadow-lg shadow-blue-400">Public</button>
                <button on:click={private_main} class="border-4 border-yellow-400 mx-auto h-1/3 w-1/3 rounded-2xl text-4xl bg-yellow-400 text-black font-bold hover:border-yellow-600 shadow-lg shadow-blue-400">Private</button>
            </div>
    </div>

    <div id="private_selector" class="absolute z-40 h-1/3 w-full hidden">
        <div class="flex rounded-2xl shadow-lg w-1/2 h-full bg-blue-600 mx-auto items-center">
            <button on:click={private_join} class="border-4 border-green-400 mx-auto h-1/3 w-1/3 rounded-2xl text-4xl bg-green-400 text-black font-bold hover:border-green-600 shadow-lg shadow-blue-400">Join</button>
            <button on:click={private_create} class="border-4 border-yellow-400 mx-auto h-1/3 w-1/3 rounded-2xl text-4xl bg-yellow-400 text-black font-bold hover:border-yellow-600 shadow-lg shadow-blue-400">Create</button>
        </div>
</div>
    <!-- svelte-ignore a11y-missing-attribute -->

<div id="main" class="w-1/4 mx-auto py-8 rounded-lg bg-[#3E63DD] border-[#435DB1] shadow-xl opacity-0 hidden app-width:block">
    <div id="main_elements" class="h-full w-full flex flex-col gap-8 justify-center items-center opacity-0">
        <div class="flex w-1/2 justify-center items-center">
            <button on:click={()=>{pfp_change('left')}} class="text-5xl font-extrabold text-blue-100 animate-pulse hover:text-stone-300 mr-auto h-fit">&lt;</button>
            <img src={current_pfp} class="border-4 size-32 rounded-full border-blue-500"/>
            <button on:click={()=>{pfp_change('right')}} class="text-5xl font-extrabold text-blue-100 animate-pulse hover:text-stone-300 ml-auto h-fit">&gt;</button>
        </div>
        <form on:submit={form_submit} class="flex flex-col items-center gap-6">
                <input id="name" required  maxlength="12" placeholder="Guest" class="bg-transparent focus:bg-none placeholder-opacity-60 placeholder-white text-2xl focus:outline-none text-white border-b-2 border-blue-300 w-2/3"/>
                <div class="cf-turnstile" data-sitekey="0x4AAAAAAAgaV_I1gnq7uKvC"></div>
                <button id="button" class="border-[3px] focus:border-blue-500 border-blue-300 px-12 py-2 w-fit text-white rounded-lg font- animate-pulse">PLAY</button>
        </form>
    </div>
</div>

</div>
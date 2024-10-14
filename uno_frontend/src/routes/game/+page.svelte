
<script>
    import { onMount } from 'svelte';
    import { gsap } from "gsap";
    import { global } from 'styled-jsx/css';
    import { goto } from '$app/navigation';
    import Layout from '../+layout.svelte';

    let game_id = null
    let socket = null
    let session_id = null
    let game_started = false
    let im_leader = false
    let wild_color = null
    let previous_turn = 'red'
    let new_turn = null
    let my_color = 'red'
    let room_type = 'private'
    let table_card = 'uno.png'
    let current_card_combo = []
    let special_cards = ['special/+4.png','special/wild.png']
    const api = import.meta.env.VITE_BACKEND_API
    const protocol = import.meta.env.VITE_SSL_BOOL == 'TRUE' ? 'wss' : 'ws';
    let global_layout = {}
    let my_party_players = {
    }
    let winner_pfp = null
    let winner_name = null
    $: player_entries = Object.entries(my_party_players);

    let deck = [
        'green/5.png',
        'red/0.png',
        'special/wild.png',
        'yellow/+2.png',
        'green/reverse.png',
        'blue/skip.png',
        'yellow/4.png',
        'green/2.png',
        'blue/4.png',
        'red/6.png',
        'special/+4.png',
        'red/4.png'
    ]
    
    fisherYatesShuffle(deck)

    let players = {
        red: {
            name: 'Red',
            cards: [],
            pfp: '',
            alt_cards: [],
        },
        green:{
            name: 'Green',
            cards: [],
            pfp: '',
            alt_cards: []
        },
        blue:{
            name: 'Blue',
            cards: [],
            pfp: '',
            alt_cards: []
        },
        yellow:{
            name: 'Yellow',
            cards: [],
            pfp: '',
            alt_cards: []
        }
    }

    function fisherYatesShuffle(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            let j = Math.floor(Math.random() * (i + 1));  
            [arr[i], arr[j]] = [arr[j], arr[i]];         
        }
        }

    function shuffleHTMLCollection(htmlCollection) {
            const array = Array.from(htmlCollection);
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
    }
    
    function splitArrayInTwo(arr) {
        const middleIndex = Math.ceil(arr.length / 2);
        const firstHalf = arr.slice(0, middleIndex);
        const secondHalf = arr.slice(middleIndex);
        return [firstHalf, secondHalf];
    }

    function capitalizeString(str) {
        if (!str) return str;
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function show_table(){
        let table = document.getElementById('table')
        table.classList.remove('opacity-0')
        gsap.from(
            table,
            {
            y:"40vh",
            opacity:0,
            duration:1,
            onComplete:(()=>{
                let my_shuffle_text = document.getElementById('shuffle_text')
                let draw_button = document.getElementById('draw_button')
                gsap.to(
                my_shuffle_text,{opacity:1,duration:2}
                )
                gsap.to(
                    draw_button,{
                        opacity:1
                    }
                )
        })})
    }
    // SHOW SHUFFLE ANIMATION AND PREPARE THE DISTRIBUTER
    function shuffle_deck(){
        let my = document.getElementById('distributer')
        let my_parent = document.getElementById('deckk')
        let my_childs = my_parent?.children
        let shuffled_array = shuffleHTMLCollection(my_childs)
        let my_arrays = splitArrayInTwo(shuffled_array)

        // SHUFFLE RIGHT
        for (let i in my_arrays[0]){
            sleep(1000*i).then(
                ()=> {
                gsap.to(
                my_arrays[0][i],
                { x:'28vh' ,zIndex:i, duration: 1 ,}
                )

            sleep(1000).then(
                ()=>{
                gsap.to(
                my_arrays[0][i],
                { x:0 ,zIndex:i, duration: 1 ,}
                )})

            })
            
            }
        // SHUFFLE LEFT
        for (let i in my_arrays[1]){

            sleep(1000*i).then(
                ()=> {
                gsap.to(
                my_arrays[1][i],
                { x:'-28vh' ,zIndex:i, duration: 1}
                )

            sleep(1000).then(()=>{
                gsap.to(
                my_arrays[1][i],
                { x:0 ,zIndex:i, duration: 1}
                )})

            })
            
            }
        sleep(my_arrays[0].length+my_arrays[1].length*1000+1000).then(()=>{
            gsap.to(
            my_parent, {rotateY:90,onComplete: ()=>{
                my_parent.className+=' hidden'
                my.classList.replace('hidden','flex')
                gsap.from(
                    my,{rotateY:-90,onComplete: ()=>{
                    let my_shuffle_text = document.getElementById('shuffle_text')
                    gsap.to(
                        my_shuffle_text,{opacity:0,duration:1,onComplete: ()=>{my_shuffle_text.hidden = true}}
                    )
                    distribute_cards_animation()
                }}
                )
            }}
            )
        })
        }


    function generate_layout(my_color){
            let my_reference_layout = {

                'bottom-0 left-0 ml-6 mb-6':
                    { 
                        cords:{x:-400,y:300},
                        sub_styles:['mb-8'],
                        // (1 means cards above profile)
                        position_mode:1,
                    },

                'left-0 ml-6 mt-6':
                    {
                        cords:{x:-400,y:-100},
                        sub_styles:['mt-8'],
                        position_mode:0
                    },

                'right-0 mr-6 mt-6':
                    {
                        cords:{x:400,y:-100},
                        sub_styles:['mt-8','grid-rtl'],
                        position_mode:0
                    },

                'bottom-0 right-0 mr-6 mb-6':
                    {
                        cords:{x:400,y:300},
                        sub_styles:['mb-8','grid-rtl'],
                        position_mode:1
                    },
            }

            const self_location = 'bottom-0 left-0 ml-6 mb-6'

            let final_layout = {

            }
            final_layout[my_color] = {
                main:
                    self_location.split(' '),
                cords:
                    my_reference_layout[self_location]['cords'],            
                show_cards:
                    my_reference_layout[self_location]['sub_styles'],
                position_mode:
                    my_reference_layout[self_location]['position_mode']

                }
            delete my_reference_layout[self_location]

            let my_aval_locations = Object.keys(my_reference_layout)
            fisherYatesShuffle(my_aval_locations)
            let left_colors = Object.keys(players).filter((color)=>color!=my_color)
            my_aval_locations.forEach(function (item, index) {
                final_layout[left_colors[index]] = {
                    main:
                        item.split(' '),
                    cords: 
                        my_reference_layout[item]['cords'],
                    show_cards:
                        my_reference_layout[item]['sub_styles'],
                    position_mode:
                        my_reference_layout[item]['position_mode']
                }
                });
            global_layout = final_layout
            place_players()
            }

    function place_players(){
        let layout = global_layout

        let red_main = document.getElementById('red_main')
        let red_show_cards = document.getElementById('red_show_cards')
        let red_profile = document.getElementById('red_profile')  
        let red_container = document.getElementById('red_container')
        let red_profile_img = document.getElementById('red_profile_img')
        let red_profile_name = document.getElementById('red_profile_name')

        let green_main = document.getElementById('green_main')
        let green_show_cards = document.getElementById('green_show_cards')
        let green_profile = document.getElementById('green_profile')
        let green_container = document.getElementById('green_container')
        let green_profile_img = document.getElementById('green_profile_img')
        let green_profile_name = document.getElementById('green_profile_name')

        let blue_main = document.getElementById('blue_main')
        let blue_show_cards = document.getElementById('blue_show_cards')
        let blue_profile = document.getElementById('blue_profile')  
        let blue_container = document.getElementById('blue_container')
        let blue_profile_img = document.getElementById('blue_profile_img')
        let blue_profile_name = document.getElementById('blue_profile_name')

        let yellow_main = document.getElementById('yellow_main')
        let yellow_show_cards = document.getElementById('yellow_show_cards')
        let yellow_profile = document.getElementById('yellow_profile');
        let yellow_container = document.getElementById('yellow_container')
        let yellow_profile_img = document.getElementById('yellow_profile_img')
        let yellow_profile_name = document.getElementById('yellow_profile_name')

        let all_cards = {
            red:{
                main: red_main,
                show_cards: red_show_cards,
                profile: red_profile,
                container: red_container,
                profile_img: red_profile_img,
                profile_name: red_profile_name
            },
            green:{
                main: green_main,
                show_cards: green_show_cards,
                profile: green_profile,
                container: green_container,
                profile_img: green_profile_img,
                profile_name: green_profile_name    
            
            },
            blue:{
                main: blue_main,
                show_cards: blue_show_cards,
                profile: blue_profile,
                container: blue_container,
                profile_img: blue_profile_img,
                profile_name: blue_profile_name

            },
            yellow:{
                main: yellow_main,
                show_cards: yellow_show_cards,
                profile: yellow_profile,
                container: yellow_container,
                profile_img: yellow_profile_img,
                profile_name: yellow_profile_name

            },
        }
        for (let color of Object.keys(all_cards)){
            for (let element of Object.keys(all_cards[color]).slice(0, -4)){
                all_cards[color][element].classList.add(...layout[color][element])
            }
            if (layout[color]['position_mode']){
                all_cards[color]['container'].insertBefore(all_cards[color]['show_cards'], all_cards[color]['profile']);
            }
            else{
                all_cards[color]['container'].insertBefore(all_cards[color]['profile'],all_cards[color]['show_cards']);
            }
            if (layout[color]['main'].includes('right-0')){
                all_cards[color]['profile'].insertBefore(all_cards[color]['profile_name'],all_cards[color]['profile_img'])
                all_cards[color]['profile'].classList.add('justify-end')
            }
            else{
                all_cards[color]['profile'].insertBefore(all_cards[color]['profile_img'],all_cards[color]['profile_name'])
            }
        }
        // ------------------------------------------
        // REMOVE HIDDEN PROPERTIES AND ANIMATE
        for (let color of Object.keys(all_cards)){
            gsap.to(
                all_cards[color]['main'],{opacity:1,duration:2,delay:8}
            )
        }
    }

    function draw_card(color, card = 'uno.png'){
        let distributer_card = document.getElementById(`distributer_card`)
        distributer_card.src = 'cards/'+card
        gsap.fromTo(
                distributer_card,
                {
                    x:0,
                    y:0,
                    opacity:1,
                    zIndex:-40
                },
                {
                    x: global_layout[color]['cords'].x,
                    y: global_layout[color]['cords'].y ,
                    duration: 1,
                    opacity:0,
                    onComplete: ()=>{
                        players[color]['cards'] = [...players[color]['cards'],card]
                        turn_manager()
                    }
                }
                    )
    }

    function game_start(){
        document.getElementById('main').className+=' hidden'

        let a = document.getElementById('game').classList.remove('hidden')
        let notify = document.getElementById('notify') 
        gsap.to(
            notify,{opacity:0,delay:2,duration:2,onComplete: ()=>{notify.classList.add('hidden')}}
            )
        sleep(5000).then(()=>{
                load_game()
            })
        
    }

    function load_game(){
        generate_layout(my_color)
        show_table()
        shuffle_deck()
    }

    function sessionCheck(){
        session_id = sessionStorage.getItem('sessionid')
        if (session_id == null){
            alert('Invalid Session')
            goto('/')
            return
        }
        game_manager()
        
    }
    
    function start_da_game(){
        socket.send(`{"session":"${session_id}","start_game":"true"}`)
    }

    async function distribute_cards_animation(){
        for (const color in players){
            await sleep(1000)
            let distributer_card = document.getElementById(`distributer_card`)
            gsap.fromTo(
                distributer_card,
                {
                    x:0,
                    y:0,
                    opacity:1
                },
                {
                    x: global_layout[color]['cords'].x,
                    y: global_layout[color]['cords'].y ,
                    duration: 1,
                    opacity:0,
                    onComplete: ()=>{
                        players[color]['cards'] = players[color]['alt_cards']
                    }
                }
                    )
            }
        await sleep(1000)
        let table_card_element = document.getElementById('table_card')
        gsap.to(
            table_card_element,
            {rotateY:90,
                onComplete:()=>{
                    table_card_element.src = 'cards/'+table_card
                    gsap.to(
                        table_card_element,
                        {rotateY:0,
                            onComplete:()=>{
                                turn_manager()
                            }
                        }
                    )
                }
            }
        )
        
        }
    // -----------------------------------------------------------------------------------------

    function throw_card_main(color, card){
        let distributer_card = document.getElementById(`distributer_card`)
        distributer_card.src = "cards/"+card
        gsap.fromTo(
                distributer_card,
                {
                    x: global_layout[color]['cords'].x,
                    y: global_layout[color]['cords'].y,
                    opacity:0
                },
                {
                    x: 0,
                    y: 0,
                    opacity: 1,
                    duration:1,
                    zIndex:40,
                    onComplete: ()=>{
                        document.getElementById('table_card').src = 'cards/'+card
                        distributer_card.opacity = 0
                        if (card.slice(-5) != 'x.png'){
                            let player_cards = players[color]['cards']
                            if (color == my_color){
                                player_cards.splice(player_cards.indexOf(card),1)
                            }
                            else{
                                player_cards.pop()
                            }
                            players[color]['cards'] = [...player_cards]
                        }
                        turn_manager()
                    }
                }
                )
    }

    function draw_card_api(){
        try {
            socket.send(`{"session":"${session_id}","action":"draw"}`)
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    async function throw_card_api(event){
        let card_or_id = event.srcElement.src.split('/').slice(-2).join('/');
        
        let sending_data = {
            session: session_id,
            action: 'throw',
            thrown: card_or_id,
            wild_color_send: null
        }

        if (special_cards.includes(card_or_id)){
            wild_color = null
            let wild_card_container = document.getElementById('wild_card_main')
            wild_card_container.hidden = false
            wild_color = await new Promise((resolve) => {
                document.getElementById('redButton').addEventListener('click', () => resolve('red'));
                document.getElementById('greenButton').addEventListener('click', () => resolve('green'));
                document.getElementById('blueButton').addEventListener('click', () => resolve('blue'));
                document.getElementById('yellowButton').addEventListener('click', () => resolve('yellow'));
            });
            sending_data['wild_color_send'] = wild_color
            wild_card_container.hidden = true
            wild_color = null
        }
        
        try {
            socket.send(JSON.stringify(sending_data))
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }   

    function show_winner(color){
        winner_name = players[color]['name']
        document.getElementById('winner').hidden = false
        alert(winner_name+' Won the Game')
        goto('/')
    }

    function game_manager(){
        socket = new WebSocket(`${protocol}://${api}/join_game?session_id=${session_id}`);
        socket.onmessage = (event) => {
        let data = JSON.parse(event.data)
            if (data.action == "self_joined"){
                my_party_players = data.players
                game_id = data.game_id
                room_type = data.room_type
                document.getElementById('main_stuff').classList.remove('opacity-0')
                if (data.leader){
                    im_leader = true
                    }
            } 
            else if (data.action == "joined"){
                let name = data.name
                let pfp = data.pfp
                my_party_players[name] = pfp
                } 

            else if (data.action == 'throw'){
                let thrown_color = data.color
                let thrown_card = data.card 
                current_card_combo = data.combo
                new_turn = data.turn
                throw_card_main(thrown_color,thrown_card)
            }
            else if (data.action == 'draw'){
                let drawn_color = data.color
                new_turn = data.turn
                draw_card(drawn_color)
            }
            else if (data.action == 'self_draw'){
                new_turn = data.turn
                draw_card(my_color,data.card)
            }
            else if (data.action == 'left'){
                let name = data.name
                delete my_party_players[name];
                my_party_players = my_party_players
                if (game_started){
                    let his_color = data.color
                    players[his_color]['name'] = 'Bot'
                }
            }
            else if (data.action == 'end'){
                show_winner(data.color)
            }
            else if (data.action == 'room_type_change'){
                room_type = data.room_type
                console.log(room_type)
            }
            else if (data.action == 'start'){
                game_started = true
                my_color = data.color
                for (let color in data.colors_data){
                    players[color].name = data.colors_data[color].name
                    players[color].pfp = data.colors_data[color].pfp
                    players[color].alt_cards = data.colors_data[color].cards
                }
                table_card = data.table_card
                new_turn = data.turn
                current_card_combo = data.combo
                    
                game_start()

                }
                
            };
            
            socket.onclose = () => {
                goto('/')
            };

            socket.onerror = () => {
                goto('/')
            };
    }

    function change_room_type(){
        socket.send(`{"session":"${session_id}","change_room_type":"true"}`)
    }

    function turn_manager(){
        let my_styles = ['border-2' ,'border-yellow-300' ,'animate-pulse'] 
        document.getElementById(previous_turn+'_container').classList.remove(...my_styles)
        document.getElementById(new_turn+'_container').classList.add(...my_styles)
        previous_turn = new_turn
    }


    onMount(() => {
        sessionCheck()
    })

</script>


<div id="main" class="flex justify-center items-center h-screen w-full bg-[#5472E4] overflow-hidden">   
    
    <div id="main_stuff" class="flex flex-col gap-12 items-center w-1/2 rounded-lg opacity-0">

        <div class="inline-flex w-1/2">
            <button disabled={!im_leader} on:click={()=>{change_room_type()}} id="public" class="bg-blue-500 {room_type == 'public' ? 'border-4 border-blue-800 bg-blue-600' : ''} {im_leader ? 'hover:bg-blue-600':''} text-stone-200 text-4xl font-bold py-4 rounded-l w-full">
              Public
            </button>
            
            <div class="border-2 border-blue-600"></div>

            <button disabled={!im_leader} on:click={()=>{change_room_type()}} id="private" class="bg-blue-500 {room_type == 'private' ? 'border-4 border-blue-800 bg-blue-600' : ''} {im_leader ? 'hover:bg-blue-600':''} text-stone-200 text-4xl font-bold py-4 rounded-r w-full">
              Private
            </button>
        </div>


        <div class="text-white text-4xl"><span class="text-red-300 font-bold">Game ID:</span> {game_id}</div>
        <button on:click={start_da_game} class="w-1/2 border-4 rounded-full border-blue-800 bg-blue-500 animate-pulse p-5 text-white text-4xl {im_leader ? '': 'hidden'}">START</button>
        <div class="grid grid-cols-2 gap-y-4 gap-x-24 h-full w-full">

            {#each player_entries as [name, pfp]}
                <div class="flex border-blue-800 items-center border-8 p-4 rounded-full h-fit bg-blue-500 ">
                    <img src={pfp} alt="" class="border-4 border-blue-600 size-24 rounded-full">
                    <div class="text-4xl font-bold text-center text-white w-full">{name}</div>
                </div>
            {/each}
            
        </div>
    </div>
</div>


<!-- --------------------------------------------------------------------------------------- -->
<!-- svelte-ignore a11y-missing-attribute -->
<div id="game" class="max-h-screen h-screen max-w-full overflow-hidden bg-[#5472E4] hidden">


    <div id="notify" class="absolute z-40 font-extrabold w-full h-full">
        <div class="flex justify-center items-center h-full w-full backdrop-blur-lg">
                <div class="border-8 p-12 animate-bounce rounded-lg bg-blue-500 text-white border-blue-600 text-8xl">STARTING</div>
        </div>
    </div>

    <div id="wild_card_main" class="absolute z-40 w-full h-screen" hidden>
        <div class="flex justify-center items-center h-full w-full backdrop-blur-xl">
            <div class="flex flex-col h-1/2 w-1/3 bg-[#4e6de8] border-[#3a5bdda8] border-4 shadow-sm shadow-black p-6">
                <div class="w-full text-center font-bold animate-pulse text-4xl text-white py-4">CHOOSE WILD COLOR</div>
                <div class="grid grid-cols-2 grid-rows-2 w-full h-full px-12 gap-4">
                    <button id="redButton" class="bg-red-400 hover:bg-red-500"/>
                    <button id="greenButton"  class="bg-green-400 hover:bg-green-500"/>
                    <button id="blueButton" class="bg-blue-400 hover:bg-blue-500"/>
                    <button id="yellowButton" class="bg-yellow-400 hover:bg-yellow-500"/>
                </div>

            </div>
        </div>

    </div>


    <div id="winner" class="absolute h-screen w-full backdrop-blur-lg hidden">
        <div class="flex flex-col p-4 h-1/2 w-1/3 rounded-lg bg-[#4e6de8] border-[#3a5bdda8] border-4">
            <div class="animate-bounce text-3xl font-bold">WINNER</div>
            <img src={winner_pfp} class="size-1/2 mx-auto"/>
            <div class="text-2xl w-full text-center">{winner_name}</div>
        </div>
    </div>


    <div class="absolute h-1/2 w-full">
        <div id="deckk" class="flex h-full w-full h justify-center items-end">
            {#each deck as card}
                <img src="cards/{card}" class="absolute rounded-[2.9rem] h-2/3 w-[14%]">
            {/each}
            
        </div>
        <div id="distributer" class="h-full w-full justify-center items-end hidden">
            <img id='table_card' src="cards/uno.png" class="z-10 rounded-[2.9rem] h-2/3 w-[14%]">
            <img id="distributer_card" src="cards/uno.png" class="absolute rounded-[2.9rem] h-2/3 w-[14%]">
                        
        </div>
    </div>

    <!-- CARDS ------------------------------ CARDS ----------------------------- CARDS---------------------------------------------- -->
     

    <div id="green_main" class="absolute w-1/5 opacity-0 border-4 rounded-lg bg-[#4e6de8] border-[#3a5bdda8]">
        <div id="green_container" class="flex flex-col rounded-lg p-2">
                <div id="green_profile" class="flex gap-6 items-center h-full w-full">
                        <img id="green_profile_img" src={players.green.pfp} alt="" class="size-20 border-[6px] border-green-400 rounded-full">
                        <div id="green_profile_name" class=" text-white text-2xl">{players['green']['name']}</div>
                </div>
                <div id="green_show_cards" class="grid-cols-7 grid-rows-3 gap-3 grid grid-flow-col-dense">
                    {#each players['green']['cards'] as card}
                        <img id={card} class="rounded-lg size-9" alt="" src="cards/{card}"/>
                    {/each}
                </div>
        </div>
    </div>


    <div id="red_main" class="absolute w-1/5 opacity-0 border-4 rounded-lg bg-[#4e6de8] border-[#3a5bdda8]">
        <div id="red_container" class="flex flex-col rounded-lg p-2">
                <div id="red_show_cards" class="grid-cols-7 grid-rows-3 gap-3 grid grid-flow-col-dense">
                    {#each players['red']['cards'] as card}
                        <img id={card} class="rounded-lg size-9" alt="" src="cards/{card}"/>
                    {/each}
                </div>
                <div id="red_profile" class="flex gap-6 items-center h-full w-full">
                        <img id="red_profile_img" src={players.red.pfp} alt="" class="size-20 border-[6px] border-red-500 rounded-full">
                        <div id="red_profile_name" class=" text-white text-2xl">{players['red']['name']}</div>
                </div>

        </div>
    </div>
    <div id="blue_main" class="absolute w-1/5 opacity-0 border-4 rounded-lg bg-[#4e6de8] border-[#3a5bdda8]">
        <div id="blue_container" class="flex flex-col p-2 rounded-lg">
                <div id="blue_profile" class="flex gap-6 items-center h-full w-full">
                        <div id="blue_profile_name" class=" text-white text-2xl">{players['blue']['name']}</div>
                        <img id="blue_profile_img" src={players.blue.pfp} alt="" class="size-20 border-[6px] border-blue-300 rounded-full">
                        
                </div>
                <div id="blue_show_cards" class="grid-cols-7 grid-rows-3 gap-3 grid grid-flow-col-dense">
                    {#each players['blue']['cards'] as card}
                        <img id={card} class="rounded-lg size-9" alt="" src="cards/{card}"/>
                    {/each}
                </div>
        </div>
    </div>
    <div id="yellow_main" class="absolute w-1/5 opacity-0 border-4 rounded-lg bg-[#4e6de8] border-[#3a5bdda8]">
        <div id="yellow_container" class="flex flex-col p-2 rounded-lg">
                <div id="yellow_show_cards" class="grid-cols-7 grid-rows-3 gap-3 grid grid-flow-col-dense">
                    {#each players['yellow']['cards'] as card}
                        <img id={card} class="rounded-lg size-9" alt="" src="cards/{card}"/>
                    {/each}
                </div>
                <div id="yellow_profile" class="flex gap-6 items-center h-full w-full">
                    <img id="yellow_profile_img" src={players.yellow.pfp} alt="" class="size-20 border-[6px] border-yellow-300 rounded-full">
                    <div id="yellow_profile_name" class="text-white text-2xl">{players['yellow']['name']}</div>
                </div>

        </div>
    </div>

    <!-- CARDS ------------------------------ CARDS ----------------------------- CARDS---------------------------------------------- -->



    <div class="absolute bottom-8 h-1/2 w-full overflow-hidden">
        <div id="shuffle_text" class="absolute z-40 w-full h-full opacity-0">
            <div class="flex w-1/2 mx-auto h-full text-7xl animate-pulse text-white font-extrabold justify-center items-center truncate">
                     SHUFFLING..
            </div>
        </div>
        <div id="draw_button" class="flex h-[20%] text-2xl font-bold text-center w-1/2 mx-auto p-2 justify-end opacity-0">
            <button 
                disabled={new_turn != my_color} 
                on:click={()=>draw_card_api()}
                class="bg-[#4e6de8] border-[#3a5bdda8] border-4 text-white h-full w-[15%] rounded-lg">
                Draw
            </button>
        </div>
        <div id="table" class="grid gap-2 grid-rows-3 grid-cols-10 w-1/2 h-full mx-auto rounded-xl border-8 bg-[#4e6de8] border-[#3a5bdda8] p-4 border-t-2 opacity-0">
            {#each players[my_color]['cards'] as card}
                    <button id={card} disabled={!((card.split('/').some(item => current_card_combo.includes(item)) || special_cards.includes(card)) && new_turn==my_color)} on:click={throw_card_api}><img class="rounded-2xl" alt="" src="cards/{card}"/></button>
            {/each}
        </div>
    </div>
</div>
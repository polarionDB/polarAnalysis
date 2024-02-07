import { Database, Game, pgnRead, Position, Variation } from 'kokopu';

type averageMovesMap = Map<number, [number, number]>;

const main = async (): Promise<void> => {
    if (Bun.argv.length != 3) {
        console.log("Input file not provided.");
        return;
    }
    
    let pgn: string | null = await Bun.file(Bun.argv[2]).text();
    let amount_of_games = 0;
    let amount_of_positions = 0;
    const db:  Database = pgnRead(pgn);
    pgn = null;

    let average_moves: [averageMovesMap, averageMovesMap] = [new Map(), new Map()];

    [...Array(db.gameCount()).keys()].forEach((game_i: number, callback: any) => {
        amount_of_games += 1;
        
        try {
            const game: Game = db.game(game_i);
            const variation: Variation = game.mainVariation();
    
            let move_n = 0;
    
            variation.nodes().map((node) => {
                const position = node.position(); 
                const colour = position.turn() === 'w' ? 0 : 1;
                const legal_moves_length: number = position.moves().length;
                
                const [amount, average] = average_moves[colour].get(move_n) ?? [0, 0.0];
                average_moves[colour].set(move_n, [amount + 1, (amount * average + legal_moves_length) / (amount + 1)]);
                
                if (colour == 1) {move_n += 1;}
                amount_of_positions += 1;
            })
        } catch (e) {
            console.log("Error '" + e + "' on Game N: " + game_i + ". Skipping");
            amount_of_games -= 1;
        };
    }, (error: any, contents: any) => {
        if (error) {throw error};
    });

    console.log("Analyzed " + amount_of_positions + " moves of " + amount_of_games + " games.");

    const white = JSON.stringify({
        x: [...average_moves[0].keys()],
        y: [...average_moves[0].values()].map(x => x[1])
    });

    const black = JSON.stringify({
        x: [...average_moves[1].keys()],
        y: [...average_moves[1].values()].map(x => x[1])
    });

    Bun.write('results/white_legal_moves.json', white);
    Bun.write('results/black_legal_moves.json', black);
};

main();
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  // For usleep()

useconds_t MICROSECOND_IN_SECOND = 1000000;

typedef enum {
    // No looping around edges
    RECTANGLE,
    // Loops around in both directions
    SPHERE,
    // Loops in both directions
    TORUS,
    // Loops in one direction
    MOBIUS,
} topology_t;

// # 2. Set up constants to aid with describing the passage directions
//
// Represent directions as a bitset
// In binary:
// N is 0b0001=1
// S is 0b0010=2
// E is 0b0100=4
// W is 0b1000=8
// Now we can combine directions to represent neighbors in a graph
// or to represent a cell in the maze that is open or accessible in zero or more directions
//
// For example, a cell that can be reached from the south and east
// is equal to: EAST | SOUTH (bitwise or)
//
// Or we can check that a bitset contains or allows a direction:
// e.g. does the variable dir contain east? This is bitwise and: dir & EAST
typedef unsigned int direction_set;

// A direction_set can represent a single directions or a group of up to 4 directions.
const direction_set EMPTY = 0, NORTH = 1, SOUTH = 2, EAST = 4, WEST = 8;

// Now what is the definition of each direction in terms of x and y?
const int DELTA_XY[9] = {
    // 0 is unused
    0,
    // North means y-1 
    // South means y+1
    -1, 1,
    // 3 is unused
    0,
    // East=4 means x-1
    1,
    // 5, 6, 7 are unused
    0, 0, 0,
    // West=8 means x+1
    -1,
};

// What is the opposite direction of a single direction?
const direction_set OPPOSITE[9] = {
    0, 2, 1, 0, 8, 0, 0, 0, 4,
};

// # 3. Data structures and functions to assist the algorithm

// Convert an x,y coordinate into an index
size_t xy_to_int(int x, int y, size_t max_x) {
    if (x < 0 || y < 0) {
        // whyyyy
        return 0;
    }
    return x + y * max_x;
}

void tty_display_maze(direction_set* grid, size_t max_x, size_t max_y) {
    // move cursor to upper left
    printf("\e[H");
    printf(" ");
    for (int i = 0; i < max_x * 2 - 1; i++) {
        printf("_");
    }
    // Print newline
    puts("");
    for (int y = 0; y < max_y; y++) {
        printf("|");
        for (int x = 0; x < max_x; x++) {
            size_t index = xy_to_int(x, y, max_x);
            direction_set cell = grid[index];

            // Print a solid block for empty or uninitialized cells with no connections to other cells
            if (cell == EMPTY) {
                printf("\e[47m");
            }

            printf("%c", (cell & SOUTH) != 0 ? ' ' : '_');

            if ((cell & EAST) != 0) {
                printf("%c", ((cell | grid[index + 1]) & SOUTH) ? ' ' : '_');
            } else {
                printf("|");
            }

            // Print a solid block for empty or uninitialized cells
            if (cell == EMPTY) {
                printf("\e[m");
            }
        }
        // Print newline
        puts("");
    }
    fflush(stdout);
}

typedef struct {
    // This will form a tree structure where we only care about the parrent
    // and each parent can have many children
    //
    // If a node has no parent, we point it to itself!
    // E.g. a root is its own parent
    //
    // In this union-find data structure,
    // the root is also known as the ultimate parent, the category, the class (not OOP), the representative of the set, or the equivalence class of the set
    size_t parent;
    // How many children does this tree have? Starts out at 1.
    size_t size;
    // My identifier, used as the parent as well
    size_t index;
} set_t;

set_t* find_root(set_t* sets, set_t* set) {
    // Also known as the find method of a union-find or disjoint set data structure.
    // 
    // Runtime is O(log n) as long as connect() keeps the sets well balanced!
    // Runtime could be made O(1), but that's more complicated and unneeded here
    //
    // Climb up the tree until the root is found
    while (set->parent != set->index) {
        set = &sets[set->parent];
    }
    return set;
}

int is_connected(set_t* sets, set_t* set1, set_t* set2) {
    // Runtime is O(log n)
    return find_root(sets, set1) == find_root(sets, set2);
}

void connect(set_t* sets, set_t* set1, set_t* set2) {
    // Also known as the union method of a union-find or disjoint set data structure.
    //
    // Runtime is O(1)

    // Find the ultimate parent of both given sets.
    set1 = find_root(sets, set1);
    set2 = find_root(sets, set2);
    if (set1 == set2) {
        return;
    }

    if (set1->size < set2->size) {
        // Swap to make sure set1 is always the biggest tree
        set_t* tmp = set1;
        set1 = set2;
        set2 = tmp;
    }
    // Add the smaller tree as a child of the bigger tree
    set2->parent = set1->index;
    set1->size += set2->size;
}

typedef struct {
    int source_x;
    int source_y;
    direction_set direction;
    int skipme;
} edge_t;

int main(int argc, char** argv) {
    printf("WELCOME!");
    // # 1. Allow the maze to be customized via command-line parameters
    //
    // Convert the integer arguments allowing any base to be used, e.g. 0x123 hexadecimal or decimal
    size_t width  = argc > 1 ? strtol(argv[1], NULL, 0) : 10;
    size_t height = argc > 2 ? strtol(argv[2], NULL, 0) : width;
    size_t seed   = argc > 3 ? strtol(argv[3], NULL, 0) : rand();
    double delay  = argc > 4 ? strtod(argv[4], NULL) : 0.01;
    int animate = argc > 5 ? 0 : 1;
    // Set the random seed
    srand(seed);

    // Allocate a grid that defines which cell is accessible from which directions
    size_t grid_size = width * height;
    direction_set* grid = calloc(grid_size, sizeof(direction_set));

    // Allocate sets.
    // Each grid cell belongs to one set.
    // Start out by adding each position to a set of size 1.
    // Kruskal's algorithm will then join the sets.
    set_t* sets = calloc(grid_size, sizeof(set_t));
    for (int i = 0; i < grid_size; i++) {
        // Identify self relative to sets array.
        sets[i].index = i;
        // This tree node is its own parent, aka it is a root!
        sets[i].parent = i;
        // This tree has just 1 node, itself.
        sets[i].size = 1;
    }

    // Allocate all necessary edges
    // TODO allocate more for any looping topologies
    // Each cell has 2 connections to its north and west neighbors
    size_t edge_count = 2 * height * width;
    edge_t* edges = calloc(edge_count, sizeof(edge_t));

    // Now define the graph :)
    // It is connected: each cells is accessible from any other cell
    // because each cell is connected to its immediate neighbors.
    //
    // It is acyclic: no loops are formed in any paths in the grid
    // because each cell only connects to the north and west.
    // 
    // First: add all north connections
    for (int e = 0; e < height * width; e++) {
        int x = e % width;
        int y = e / height;
        if (y == 0) edges[e].skipme = 1;
        edges[e].source_x = x;
        edges[e].source_y = y;
        edges[e].direction = NORTH;
    }
    // Second: add all west connections
    for (int e = height * width; e < 2 * height * width; e++) {
        int x = (e - (height * width)) % width;
        int y = (e - (height * width)) / height;
        if (x == 0) edges[e].skipme = 1;
        edges[e].source_x = x;
        edges[e].source_y = y;
        edges[e].direction = WEST;
    }

    // # 4. Kruskal's algorithm

    // First, randomize the list of edges.
    // This is equivalent to giving each edge a random weight in the typical Kruskal's algorithm.
    // Use Knuth's shuffling algorithm.
    for (int e = 0; e < edge_count; e++) {
        int other_e = rand() % edge_count;
        edge_t edge = edges[e];
        edge_t other = edges[other_e];
        edges[e] = other;
        edges[other_e] = edge;
    }

    // Clear the screen
    printf("\e[2J");

    for (int e = 0; e < edge_count; e++) {
        edge_t edge = edges[e];

        if (edge.skipme) continue;

        // Find the other edge
        size_t other_x = edge.source_x + DELTA_XY[edge.direction];
        size_t other_y = edge.source_y + DELTA_XY[edge.direction];
        size_t edge_i = xy_to_int(edge.source_x, edge.source_y, width);
        size_t other_i = xy_to_int(other_x, other_y, width);
        
        set_t* set1 = &sets[edge_i];
        set_t* set2 = &sets[other_i];
        // If these two positions aren't in the same set (the same ball of clay)
        // Then join them and open the wall in this edge's direction.
        if (!is_connected(sets, set1, set2)) {
            if (animate) {
                tty_display_maze(grid, width, height);
                usleep(delay * MICROSECOND_IN_SECOND);
            }

            connect(sets, set1, set2);
            // Record that this cell in the grid is open in the given direction...
            // Use bitwise or | to add a direction to this cell in the grid
            grid[edge_i] |= edge.direction;
            // Record that the other cell in the grid is open in the opposite direction...
            grid[other_i] |= OPPOSITE[edge.direction];
        }
    }
    tty_display_maze(grid, width, height);
    // # 5. Show the parameters used to build this maze, for repeatability
    printf("\n%s %zux%zu seed=%zu\n", argv[0], width, height, seed);
    free(grid);
    free(sets);
    free(edges);
    return 0;
}

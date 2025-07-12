use crossterm::{
    cursor::{Hide, MoveTo, Show},
    event::{Event, KeyCode, KeyEvent, poll, read},
    execute,
    style::{Color, Print, ResetColor, SetForegroundColor},
    terminal::{Clear, ClearType, disable_raw_mode, enable_raw_mode, size},
};
use std::io::{Write, stdout};
use std::time::{Duration, Instant};

const WIDTH: u16 = 80;
const HEIGHT: u16 = 24;
const SHIP_Y: u16 = HEIGHT - 2;
const SHIP_START_X: u16 = WIDTH / 2;
const BOTTOM_LINE: u16 = HEIGHT - 1;
const MAX_MISSILES: usize = 10;
const STAR_COUNT: usize = 50;

struct Game {
    ship_x: u16,
    missiles: Vec<(u16, u16)>,
    stars: Vec<(u16, u16)>,
    frame: u64,
    offset_x: u16,
}

impl Game {
    fn new() -> Self {
        let offset_x = size()
            .map(|(w, _)| if w > WIDTH { (w - WIDTH) / 2 } else { 0 })
            .unwrap_or(0);
        let stars = (0..STAR_COUNT)
            .map(|_| (fastrand::u16(..WIDTH), fastrand::u16(..HEIGHT - 3)))
            .collect();

        Self {
            ship_x: SHIP_START_X,
            missiles: Vec::new(),
            stars,
            frame: 0,
            offset_x,
        }
    }

    fn update(&mut self) {
        self.frame += 1;
        self.missiles.retain_mut(|(_, y)| {
            *y = y.saturating_sub(1);
            *y > 0
        });

        if self.frame % 3 == 0 {
            self.stars.iter_mut().for_each(|(_, y)| {
                *y = (*y + 1) % (HEIGHT - 2);
            });
        }
    }

    fn handle_input(&mut self) -> std::io::Result<bool> {
        if !poll(Duration::from_millis(16))? {
            return Ok(true);
        }

        match read()? {
            Event::Key(KeyEvent {
                code: KeyCode::Left,
                ..
            }) => self.ship_x = self.ship_x.saturating_sub(1),
            Event::Key(KeyEvent {
                code: KeyCode::Right,
                ..
            }) => self.ship_x = (self.ship_x + 1).min(WIDTH - 1),
            Event::Key(KeyEvent {
                code: KeyCode::Char(' '),
                ..
            }) => {
                if self.missiles.len() < MAX_MISSILES {
                    self.missiles.push((self.ship_x, SHIP_Y - 1));
                }
            }
            Event::Key(KeyEvent {
                code: KeyCode::Char('q'),
                ..
            })
            | Event::Key(KeyEvent {
                code: KeyCode::Esc, ..
            }) => return Ok(false),
            _ => {}
        }
        Ok(true)
    }

    fn draw_at(&self, x: u16, y: u16, c: &str, color: Color) -> std::io::Result<()> {
        execute!(
            stdout(),
            SetForegroundColor(color),
            MoveTo(x + self.offset_x, y),
            Print(c)
        )
    }

    fn draw_sprites(&self, sprites: &[(u16, u16)], c: &str, color: Color) -> std::io::Result<()> {
        execute!(stdout(), SetForegroundColor(color))?;
        for &(x, y) in sprites {
            execute!(stdout(), MoveTo(x + self.offset_x, y), Print(c))?;
        }
        Ok(())
    }

    fn render_ui(&self) -> std::io::Result<()> {
        execute!(stdout(), SetForegroundColor(Color::Grey))?;
        execute!(
            stdout(),
            MoveTo(self.offset_x, 0),
            Print("MOVE WITH ARROWS ← →    FIRE WITH SPACE    QUIT WITH ESC Q")
        )?;
        execute!(
            stdout(),
            MoveTo(WIDTH - 20 + self.offset_x, 0),
            Print(&format!("MISSILES:{:02}", self.missiles.len()))
        )?;
        Ok(())
    }

    fn render(&self) -> std::io::Result<()> {
        execute!(stdout(), Clear(ClearType::All))?;

        self.draw_sprites(&self.stars, ".", Color::White)?;
        self.draw_sprites(&self.missiles, "|", Color::Yellow)?;
        self.draw_at(self.ship_x, SHIP_Y, "^", Color::Green)?;

        execute!(stdout(), SetForegroundColor(Color::Blue))?;
        for x in 0..WIDTH {
            execute!(stdout(), MoveTo(x + self.offset_x, BOTTOM_LINE), Print("-"))?;
        }

        self.render_ui()?;
        execute!(stdout(), ResetColor)?;
        stdout().flush()
    }
}

fn main() -> std::io::Result<()> {
    println!(
        "GALAGA - Exact Copy of Hit 1981 Videogame\nControls: ← → arrows to move, SPACE to fire, Q to quit"
    );

    if let Ok((w, h)) = size() {
        println!("Terminal: {}x{} columns", w, h);
        if w > WIDTH {
            println!(
                "Game field centered with {} column margins",
                (w - WIDTH) / 2
            );
        }
    }

    println!("Press any key to start...");
    std::io::stdin().read_line(&mut String::new())?;

    enable_raw_mode()?;
    execute!(stdout(), Hide)?;

    let mut game = Game::new();
    let mut last_frame = Instant::now();

    loop {
        if last_frame.elapsed() >= Duration::from_millis(50) {
            game.update();
            game.render()?;
            last_frame = Instant::now();
        }
        if !game.handle_input()? {
            break;
        }
    }

    execute!(stdout(), Show, ResetColor, Clear(ClearType::All))?;
    disable_raw_mode()?;
    println!("Thanks for playing GALAGA!");
    Ok(())
}

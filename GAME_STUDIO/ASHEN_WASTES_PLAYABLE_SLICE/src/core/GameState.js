export class GameState {
  reset(){
    this.hp = 100;
    this.stamina = 100;
    this.inLava = false;
    this.bossStarted = false;
    this.bossHp = 100;
    this.kills = 0;
  }
}

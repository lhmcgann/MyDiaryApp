import React, { Component } from "react";
import DiaryList from "./DiaryList";
import DiaryButton from './DiaryButton'
import axios from "axios";
import './styles.css'
import { Link } from "react-router-dom";
import Button from "react-bootstrap/Button";
class App extends Component {
  state = {
    characters: [
      { name: "My Diary 1", id: "i204847w20s"},
      { name: "My Diary 2", id: "2jksfnwoen2" },
      { name: "My Diary 3", id: "nviq9h29fiqh" },
      { name: "My Diary 4", id: "o31j03ijrf0i" },
    ],
  };
  handleSubmit = character => {
    this.setState({ characters: [...this.state.characters, character] })
  }
  render() {
    const { characters } = this.state;
    return (
      <div class="centered">
        <h1>Welcome to MyDiary</h1>
        <DiaryList characterData={characters} />
        <DiaryButton handleSubmit={this.handleSubmit} />
      </div>
    );
  }
}
export default App;

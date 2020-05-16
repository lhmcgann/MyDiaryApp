import React, { Component } from "react";
import DiaryList from "./DiaryList";
import DiaryButton from "./DiaryButton";
import axios from "axios";
import "./styles.css";
import { Link } from "react-router-dom";
import Button from "react-bootstrap/Button";
class App extends Component {
  state = {
    characters: [],
  };
  handleSubmit = (character) => {
    this.setState({ characters: [...this.state.characters, character] });
  };
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

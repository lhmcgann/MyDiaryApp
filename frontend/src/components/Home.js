import React, { Component } from "react";
import DiaryList from "./DiaryList";
import DiaryButton from "./DiaryButton";
import axios from "axios";
class Home extends Component {

  state = { characters: [] };

  componentDidMount() {
    axios
      .get("http://localhost:5000/diaries")
      .then((res) => {
        const characters = res.data; //.diaries;
        this.setState({ characters });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  handleSubmit = (title) => {
    this.makePostCall(title).then((callResult) => {
      if (callResult !== false) {
        this.setState({ characters: [...this.state.characters, callResult] });
      }
    });
  };
  makePostCall(title) {
    return axios
      .post("http://localhost:5000/diaries", title)
      .then(function (response) {
        console.log(response);
        response.status = 201;
        return response.data;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  makeDeleteCall(character){
    return axios.delete('http://localhost:5000/diaries/'+character.id)
    .then(function (response) {
      console.log(response);
      return true;
    })
    .catch(function (error) {
      console.log(error);
      return false;
    });
  }
  removeCharacter = index => {
    const {characters} = this.state;
    const character = characters[index];
    this.makeDeleteCall(character).then((callResult) => {
      if (callResult !== false){
        this.setState({
          characters: characters.filter((character, i) => {
            return i !== index
          }),
        })
      }
    });
  }
  render() {
    const { characters } = this.state;
    return (
      <div className="centered">
        <h1>Welcome to MyDiary</h1>
        <DiaryList characterData={characters} removeCharacter={this.removeCharacter}/>
        <DiaryButton handleSubmit={this.handleSubmit}/>
      </div>
    );
  }
}
export default Home;

import React, { Component } from "react";
import EntryList from "./EntryList";
import EntryButton from "./EntryButton";
import axios from "axios";
class DiaryHome extends Component {
  state = {title: '', entries: []};
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.d_id)
      .then((res) => {
        const diary = res.data; //.diaries;
        this.setState({ title: diary.title, entries: diary.entries});
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  handleSubmit = (entry) => {
    this.makePostCall(entry).then((callResult) => {
      if (callResult !== false) {
        this.setState({ entries: [...this.state.entries, callResult] });
      }
    });
  };
  makePostCall(title) {
    return axios
      .post("http://localhost:5000/diaries/"+this.props.match.params.id+"/entries", title)
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
  render() {
    const title = this.state.title;
    const entries = this.state.entries;
    return (
      <div className="centered">
        <h1>{title}</h1>
            <EntryButton handleSubmit={this.handleSubmit}/>
            <EntryList entryData={entries}/>
      </div>
    );
  }
}
export default DiaryHome;

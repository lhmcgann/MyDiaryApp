import React, { Component } from "react";
import "../styles.css";
import axios from "axios";
class ViewEntry extends Component {
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.d_id+"/entries/"
          +this.props.match.params.e_id)
      .then((res) => {
        const entry = res.data;
        this.setState({ title: entry.title, text: entry.text});
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
state = {title: '', text: '',};
handleChange(e) {
    this.setState({
      text :e.target.value
    });
  }
render() {
 const title = this.state.title;
 const textBody = this.state.text;
 return (
   <div className="centered">
   <h1>{title}</h1>
   <textarea
    cols="30"
    rows="15"
    value={textBody}
    onChange={e => this.handleChange(e)}
   />
   </div>
  );
  }
}
export default ViewEntry;

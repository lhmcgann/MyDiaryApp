import React from "react";
import { Link } from "react-router-dom";
const DiaryListBody = (props) => {
  const rows = props.characterData.map((row, index) => {
    return (
      <div className="centered">
        <h5 key={index}>
          <Link to={`diaries/${row.id}`}>
            <button class="diary-block">{row.title}</button>
          </Link>
          <button onClick={() => props.removeCharacter(index)}>Delete</button>
        </h5>
      </div>
    );
  });
  return <tbody>{rows}</tbody>;
};
const DiaryList = (props) => {
  const { characterData, removeCharacter} = props;
  return (
    <table>
      <DiaryListBody characterData={characterData} removeCharacter={removeCharacter} />
    </table>
  );
};
export default DiaryList;

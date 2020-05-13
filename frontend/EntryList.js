import React, { Component } from 'react'
import { Link } from 'react-router-dom';
const EntryListBody = props => {

  const rows = props.entryData.map((row, index) => {
    return (
      <tr key={index}>
          <td>
            <div class="button1">
              <Link to="/entry/:id"><button class="button1">{row.name}</button></Link>
            </div>
          </td>
     </tr>
    )
  })

  return <tbody>{rows}</tbody>
}
const EntryList = props => {
  const { entryData, removeCharacter } = props

  return (

    <table>
      <EntryListBody entryData={entryData} removeCharacter={removeCharacter} />
    </table>

  )
}
export default EntryList
